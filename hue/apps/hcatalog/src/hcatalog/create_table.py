# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Views & controls for creating tables
"""

from django.core import urlresolvers

from desktop.lib import django_mako, i18n
from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.django_forms import MultiForm
from hadoop.fs import hadoopfs

import hcatalog.common
import hcatalog.forms
from hcatalog.views import _get_table_list
from hcat_client import hcat_client
from desktop.context_processors import get_app_name

import logging
import gzip
import csv
import StringIO
from datetime import datetime
import os.path

LOG = logging.getLogger(__name__)


def create_table(request, database='default'):
  """Create a table by specifying its attributes manually"""
  form = MultiForm(
    table=hcatalog.forms.CreateTableForm,
    columns=hcatalog.forms.ColumnTypeFormSet,
    partitions=hcatalog.forms.PartitionTypeFormSet)
  if request.method == "POST":
    form.bind(request.POST)
    form.table.table_list = _get_table_list(request)
    if form.is_valid() and 'createTable' in request.POST:
      columns = [f.cleaned_data for f in form.columns.forms]
      partition_columns = [f.cleaned_data for f in form.partitions.forms]
      proposed_query = django_mako.render_to_string("create_table_statement.mako",
        {
          'database': database,
          'table': form.table.cleaned_data,
          'columns': columns,
          'partition_columns': partition_columns
        }
      )
      # Mako outputs bytestring in utf8
      proposed_query = proposed_query.decode('utf-8')
      tablename = form.table.cleaned_data['name']
      tables = []
      try:
        hcat_client().create_table("default", proposed_query)
        tables = _get_table_list(request)
      except Exception, ex:
        raise PopupException('Error on creating table', title="Error on creating table", detail=str(ex))
      return render("show_tables.mako", request, dict(database=database, tables=tables,))
  else:
    form.bind()
  return render("create_table_manually.mako", request, dict(
      action="#",
      database=database,
      table_form=form.table,
      columns_form=form.columns,
      partitions_form=form.partitions,
  ))


IMPORT_PEEK_SIZE = 8192
IMPORT_MAX_SIZE = 4294967296 # 4 gigabytes
IMPORT_PEEK_NLINES = 10
DELIMITERS = [hive_val for hive_val, _, _ in hcatalog.common.TERMINATORS]
DELIMITER_READABLE = {'\\001': 'ctrl-As',
                      '\\002': 'ctrl-Bs',
                      '\\003': 'ctrl-Cs',
                      '\\t': 'tabs',
                      ',': 'commas',
                      ' ': 'spaces'}
FILE_READERS = []


def import_wizard(request, database='default'):
  """
  Help users define table and based on a file they want to import to Hive.
  Limitations:
    - Rows are delimited (no serde).
    - No detection for map and array types.
    - No detection for the presence of column header in the first row.
    - No partition table.
    - Does not work with binary data.
  """
  encoding = i18n.get_site_encoding()

  if request.method == 'POST':
    # Have a while loop to allow an easy way to break
    for _ in range(1):
      #
      # General processing logic:
      # - We have 3 steps. Each requires the previous.
      #   * Step 1      : Table name and file location
      #   * Step 2a     : Display sample with auto chosen delim
      #   * Step 2b     : Display sample with user chosen delim (if user chooses one)
      #   * Step 3      : Display sample, and define columns
      # - Each step is represented by a different form. The form of an earlier step
      #   should be present when submitting to a later step.
      # - To preserve the data from the earlier steps, we send the forms back as
      #   hidden fields. This way, when users revisit a previous step, the data would
      #   be there as well.
      #
      delim_is_auto = False
      fields_list, n_cols = [[]], 0
      s3_col_formset = None
      col_names = []

      table_list = _get_table_list(request)
      # Everything requires a valid file form
      s1_file_form = hcatalog.forms.CreateByImportFileForm(request.POST, table_list=table_list)
      if not s1_file_form.is_valid():
        break

      do_s2_auto_delim = request.POST.get('submit_file')        # Step 1 -> 2
      do_s2_user_delim = request.POST.get('submit_preview')     # Step 2 -> 2
      do_s3_column_def = request.POST.get('submit_delim')       # Step 2 -> 3
      do_hive_create = request.POST.get('submit_create')        # Step 3 -> execute

      cancel_s2_user_delim = request.POST.get('cancel_delim')   # Step 2 -> 1
      cancel_s3_column_def = request.POST.get('cancel_create')  # Step 3 -> 2

      # Exactly one of these should be True
      assert len(filter(None, (do_s2_auto_delim,
          do_s2_user_delim,
          do_s3_column_def,
          do_hive_create,
          cancel_s2_user_delim,
          cancel_s3_column_def))) == 1, 'Invalid form submission'

      s2_delim_form = None
      #
      # Fix up what we should do in case any form is invalid
      #
      if not do_s2_auto_delim:
        # We should have a valid delim form
        s2_delim_form = hcatalog.forms.CreateByImportDelimForm(request.POST)
        if not s2_delim_form.is_valid():
          # Go back to picking delimiter
          do_s2_user_delim, do_s3_column_def, do_hive_create = True, False, False

      if do_hive_create:
        # We should have a valid columns formset
        s3_col_formset = hcatalog.forms.ColumnTypeFormSet(prefix='cols', data=request.POST)
        if not s3_col_formset.is_valid():
          # Go back to define columns
          do_s3_column_def, do_hive_create = True, False

      #
      # Go to step 2: We've just picked the file. Preview it.
      #
      if do_s2_auto_delim:
        delim_is_auto = True
        fields_list, n_cols, col_names, s2_delim_form = _delim_preview(
            request.fs,
            s1_file_form,
            encoding,
            [reader.TYPE for reader in FILE_READERS],
            DELIMITERS,
            True,
            False,
            None)

      if (do_s2_user_delim or do_s3_column_def or cancel_s3_column_def) and s2_delim_form.is_valid():
        # Delimit based on input
        fields_list, n_cols, col_names, s2_delim_form = _delim_preview(
            request.fs,
            s1_file_form,
            encoding,
            (s2_delim_form.cleaned_data['file_type'],),
            (s2_delim_form.cleaned_data['delimiter'],),
            s2_delim_form.cleaned_data.get('parse_first_row_as_header'),
            s2_delim_form.cleaned_data.get('apply_excel_dialect'),
            s2_delim_form.cleaned_data['path_tmp'])
      if do_s2_auto_delim or do_s2_user_delim or cancel_s3_column_def:
        return render('choose_delimiter.mako', request, dict(
            action=urlresolvers.reverse(get_app_name(request) + ':import_wizard', kwargs={'database': database}),
            delim_readable=DELIMITER_READABLE.get(s2_delim_form['delimiter'].data[0], s2_delim_form['delimiter'].data[1]),
            initial=delim_is_auto,
            file_form=s1_file_form,
            delim_form=s2_delim_form,
            fields_list=fields_list,
            delimiter_choices=hcatalog.forms.TERMINATOR_CHOICES,
            col_names=col_names,
            database=database,
        ))

      #
      # Go to step 3: Define column.
      #
      if do_s3_column_def:
        if s3_col_formset is None:
          columns = []
          for col_name in col_names:
            columns.append(dict(
                column_name=col_name,
                column_type='string',
            ))

          s3_col_formset = hcatalog.forms.ColumnTypeFormSet(prefix='cols', initial=columns)
        return render('define_columns.mako', request, dict(
            action=urlresolvers.reverse(get_app_name(request) + ':import_wizard', kwargs={'database': database}),
            file_form=s1_file_form,
            delim_form=s2_delim_form,
            column_formset=s3_col_formset,
            fields_list=fields_list,
            n_cols=n_cols,
            database=database,
        ))

      #
      # Finale: Execute
      #
      if do_hive_create:
        delim = s2_delim_form.cleaned_data['delimiter']
        if not filter(lambda val: val[0] == delim, hcatalog.forms.TERMINATOR_CHOICES) and \
                        len(delim) > 0 and delim[0] != '\\':
          delim = '\\' + delim
        table_name = s1_file_form.cleaned_data['name']
        proposed_query = django_mako.render_to_string("create_table_statement.mako",
          {
            'table': dict(name=table_name,
                          comment=s1_file_form.cleaned_data['comment'],
                          row_format='Delimited',
                          field_terminator=delim),
            'columns': [f.cleaned_data for f in s3_col_formset.forms],
            'partition_columns': [],
            'database': database,
          }
        )

        do_load_data = s1_file_form.cleaned_data.get('do_import')
        path = s1_file_form.cleaned_data['path']
        path_tmp = s2_delim_form.cleaned_data['path_tmp']
        if request.fs.exists(path_tmp):
          if do_load_data:
            request.fs.copyfile(path_tmp, path)
            request.fs.remove(path_tmp)
          else:
            request.fs.remove(path_tmp)
        return _submit_create_and_load(request, proposed_query, database, table_name, path, do_load_data)
  else:
    s1_file_form = hcatalog.forms.CreateByImportFileForm()

  return render('choose_file.mako', request, dict(
    database=database,
    action=urlresolvers.reverse(get_app_name(request) + ':import_wizard', kwargs={'database': database}),
    file_form=s1_file_form,
  ))


def _submit_create_and_load(request, create_hql, database, table_name, path, do_load):
  """
  Submit the table creation, and setup the load to happen (if ``do_load``).
  """
  tables = []
  try:
    hcat_client().create_table(database, create_hql)
    tables = _get_table_list(request)
  except Exception, ex:
    raise PopupException('Error on creating and loading table',
        title="Error on creating and loading table", detail=str(ex))
  if do_load:
    if not table_name or not path:
      msg = 'Internal error: Missing needed parameter to load data into table'
      LOG.error(msg)
      raise PopupException(msg)
    LOG.debug("Auto loading data from %s into table %s" % (path, table_name))
    hql = "LOAD DATA INPATH '%s' INTO TABLE `%s`" % (path, table_name)
    hcatalog.views.do_load_table(request, hql)
  return render("show_tables.mako", request, dict(database=database, tables=tables,))


def _delim_preview(fs, file_form, encoding, file_types, delimiters, parse_first_row_as_header, apply_excel_dialect, path_tmp):
  """
  _delim_preview(fs, file_form, encoding, file_types, delimiters, parse_first_row_as_header, apply_excel_dialect, path_tmp)
                              -> (fields_list, n_cols, delim_form)

  Look at the beginning of the file and parse it according to the list of
  available file_types and delimiters.
  """
  assert file_form.is_valid()

  path = file_form.cleaned_data['path']
  if path_tmp is None:
    path_tmp = "/tmp/%s.tmp.%s" % (os.path.basename(path).replace(' ', ''), datetime.now().strftime("%s"))
  try:
    file_obj = fs.open(path)
    delim, file_type, fields_list = _parse_fields(
              fs, path, file_obj, encoding, file_types, delimiters, parse_first_row_as_header, apply_excel_dialect, path_tmp)
    file_obj.close()
  except IOError, ex:
    msg = "Failed to open file '%s': %s" % (path, ex)
    LOG.exception(msg)
    raise PopupException(msg)
  except Exception:
    import traceback
    error = traceback.format_exc()
    raise PopupException('Delimiter preview exception', title="Delimiter preview exception", detail=error)

  col_names = []
  n_cols = max([len(row) for row in fields_list])

  # making column list and preview data part
  if parse_first_row_as_header and len(fields_list) > 0:
    col_names = fields_list[0]
    fields_list = fields_list[1:IMPORT_PEEK_NLINES]
    if len(col_names) < n_cols:
      for i in range(len(col_names) + 1, n_cols + 1):
        col_names.append('col_%s' % (i,))
  elif not parse_first_row_as_header:
    for i in range(1, n_cols + 1):
      col_names.append('col_%s' % (i,))

  # ``delimiter`` is a MultiValueField. delimiter_0 and delimiter_1 are the sub-fields.
  delimiter_0 = delim
  delimiter_1 = ''
  # If custom delimiter
  if not filter(lambda val: val[0] == delim, hcatalog.forms.TERMINATOR_CHOICES):
    delimiter_0 = '__other__'
    delimiter_1 = delim

  delim_form = hcatalog.forms.CreateByImportDelimForm(dict(delimiter_0=delimiter_0,
      delimiter_1=delimiter_1,
      file_type=file_type,
      path_tmp=path_tmp,
      n_cols=n_cols,
      col_names=col_names,
      parse_first_row_as_header=parse_first_row_as_header,
      apply_excel_dialect=apply_excel_dialect))
  if not delim_form.is_valid():
    assert False, _('Internal error when constructing the delimiter form: %(error)s' % {'error': delim_form.errors})
  return fields_list, n_cols, col_names, delim_form


def unicode_csv_reader(encoding, unicode_csv_data, dialect=csv.excel, **kwargs):
  csv_reader = csv.reader(custom_csv_encoder(encoding, unicode_csv_data), dialect=dialect, **kwargs)
  for row in csv_reader:
    yield [unicode(cell, encoding) for cell in row]


def custom_csv_encoder(encoding, unicode_csv_data):
  for line in unicode_csv_data:
    yield line.encode(encoding)


def _parse_fields(fs, path, file_obj, encoding, filetypes, delimiters, parse_first_row_as_header, apply_excel_dialect, path_tmp):
  """
  _parse_fields(fs, path, file_obj, encoding, filetypes, delimiters, parse_first_row_as_header, apply_excel_dialect, path_tmp)
                                  -> (delimiter, filetype, fields_list)

  Go through the list of ``filetypes`` (gzip, text) and stop at the first one
  that works for the data. Then apply the list of ``delimiters`` and pick the
  most appropriate one.
  ``path`` is used for debugging only.

  Return the best delimiter, filetype and the data broken down into rows of fields.
  """
  file_readers = [reader for reader in FILE_READERS if reader.TYPE in filetypes]

  for reader in file_readers:
    LOG.debug("Trying %s for file: %s" % (reader.TYPE, path))
    file_obj.seek(0, hadoopfs.SEEK_SET)
    lines = reader.readlines(file_obj, encoding)
    if lines is not None:
      delim, fields_list = _readfields(lines, delimiters)

      # creating tmp file to import data from
      if fs.exists(path_tmp):
        fs.remove(path_tmp)
      if parse_first_row_as_header or apply_excel_dialect:
        try:
          csvfile_tmp = fs.open(path_tmp, 'w')
          file_obj.seek(0, hadoopfs.SEEK_SET)
          all_data = reader.read_all_data(file_obj, encoding)
          if apply_excel_dialect:
            csv_content = unicode_csv_reader(encoding, StringIO.StringIO('\n'.join(all_data)), delimiter=delim.decode('string_escape'))
            new_fields_list = []
            data_to_store = []
            for row in csv_content:
              new_row = []
              for field in row:
                new_row.append(field.replace(delim.decode('string_escape'), ''))
              data_to_store.append(delim.decode('string_escape').join(new_row))
              new_fields_list.append(new_row)
            fields_list = new_fields_list[:IMPORT_PEEK_NLINES]
          if parse_first_row_as_header:
            if apply_excel_dialect:
              all_data = data_to_store
            reader.write_all_data(csvfile_tmp, '\n'.join(all_data[1:]))
          else:
            reader.write_all_data(csvfile_tmp, '\n'.join(all_data))
          csvfile_tmp.close()
        except IOError, ex:
          msg = "Failed to open file '%s': %s" % (path, ex)
          LOG.exception(msg)

      return delim, reader.TYPE, fields_list
  else:
    # Even TextFileReader doesn't work
    msg = "Failed to decode file '%s' into printable characters under %s" % (path, encoding,)
    LOG.error(msg)
    raise PopupException(msg)


def _readfields(lines, delimiters):
  """
  readfields(lines, delimiters) -> (delim, a list of lists of fields)

  ``delimiters`` is a list of escaped characters, e.g. r'\\t', r'\\001', ','

  Choose the best delimiter from the given list of delimiters. Return that delimiter
  and the fields parsed by using that delimiter.
  """
  def score_delim(fields_list):
    """
    How good is this fields_list? Score based on variance of the number of fields
    The score is always non-negative. The higher the better.
    """
    n_lines = len(fields_list)
    len_list = [len(fields) for fields in fields_list]

    # All lines should break into multiple fields
    if min(len_list) == 1:
      return 0

    avg_n_fields = sum(len_list) / n_lines
    sq_of_exp = avg_n_fields * avg_n_fields

    len_list_sq = [l * l for l in len_list]
    exp_of_sq = sum(len_list_sq) / n_lines
    var = exp_of_sq - sq_of_exp
    # Favour more fields
    return (1000.0 / (var + 1)) + avg_n_fields

  max_score = -1
  res = (None, None)
  for delim in delimiters:
    fields_list = []
    for line in lines:
      if line:
        # Unescape the delimiter back to its character value
        fields_list.append(line.split(delim.decode('string_escape')))
    score = score_delim(fields_list)
    LOG.debug("'%s' gives score of %s" % (delim, score))
    if score > max_score:
      max_score = score
      res = (delim, fields_list)
  return res


def _peek_file(fs, file_form):
  """_peek_file(fs, file_form) -> (path, initial data)"""
  try:
    path = file_form.cleaned_data['path']
    file_obj = fs.open(path)
    file_head = file_obj.read(IMPORT_PEEK_SIZE)
    file_obj.close()
    return (path, file_head)
  except IOError, ex:
    msg = "Failed to open file '%s': %s" % (path, ex)
    LOG.exception(msg)
    raise PopupException(msg)


class GzipFileReader(object):
  """Class for extracting lines from a gzipped file"""
  TYPE = 'gzip'

  @staticmethod
  def readlines(fileobj, encoding):
    """readlines(fileobj, encoding) -> list of lines"""
    gz = gzip.GzipFile(fileobj=fileobj, mode='rb')
    try:
      data = gz.read(IMPORT_PEEK_SIZE)
    except IOError:
      return None
    try:
      return unicode(data, encoding, errors='ignore').splitlines()[:IMPORT_PEEK_NLINES]
    except UnicodeError:
      return None

  @staticmethod
  def read_all_data(fileobj, encoding):
    """read_all_data(fileobj, encoding) -> list of lines"""
    gz = gzip.GzipFile(fileobj=fileobj, mode='rb')
    try:
      data = gz.read()
    except IOError:
      return None
    try:
      return unicode(data, encoding, errors='ignore').splitlines()
    except UnicodeError:
      return None

  @staticmethod
  def write_all_data(fileobj, data):
    try:
      data = data.encode('ascii', 'ignore')
      try:
        gz = gzip.GzipFile(fileobj=fileobj, mode='wb')
        gz.write(data)
      except IOError:
        pass
    except UnicodeError:
      pass
FILE_READERS.append(GzipFileReader)


class TextFileReader(object):
  """Class for extracting lines from a regular text file"""
  TYPE = 'text'

  @staticmethod
  def readlines(fileobj, encoding):
    """readlines(fileobj, encoding) -> list of lines"""
    try:
      data = fileobj.read(IMPORT_PEEK_SIZE)
      return unicode(data, encoding, errors='ignore').splitlines()[:IMPORT_PEEK_NLINES]
    except UnicodeError:
      return None

  @staticmethod
  def read_all_data(fileobj, encoding):
    """read_all_data(fileobj, encoding) -> list of lines"""
    try:
      data = fileobj.read(IMPORT_MAX_SIZE)
    except IOError:
      return None
    try:
      return unicode(data, encoding, errors='ignore').splitlines()
    except UnicodeError:
      return None

  @staticmethod
  def write_all_data(fileobj, data):
    try:
      data = data.encode('ascii', 'ignore')
      try:
        fileobj.write(data)
      except IOError:
        pass
    except UnicodeError:
      pass

FILE_READERS.append(TextFileReader)
