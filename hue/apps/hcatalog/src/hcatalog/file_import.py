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


from django.core import urlresolvers

from desktop.lib import django_mako, i18n
from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.django_forms import MultiForm
from desktop.context_processors import get_app_name
from hadoop.fs import hadoopfs
from django.forms import ValidationError
from django.http import HttpResponse


import hcatalog.common
import hcatalog.forms
from hcatalog.views import _get_table_list
from hcat_client import hcat_client

import logging
import gzip
import csv
import StringIO
from datetime import datetime
import os.path
import simplejson as json
import re

LOG = logging.getLogger(__name__)


def create_from_file(request, database='default'):
    """Create a table by import from file"""
    form = MultiForm(
        table=hcatalog.forms.CreateTableFromFileForm,
        # columns=hcatalog.forms.ColumnTypeFormSet,
        # partitions=hcatalog.forms.PartitionTypeFormSet
    )
    if request.method == "POST":
        form.bind(request.POST)

        action = request.POST.get('action')
        if form.is_valid():
            do_import_data = form.table.cleaned_data['import_data']
            path = form.table.cleaned_data['path']
            encoding = form.table.cleaned_data['encoding']
            file_type = form.table.cleaned_data['file_type']

            if action == 'submitPreview':
                preview_results = {}
                preview_table_resp = ''
                fields_list, n_cols, col_names = ([], 0, [])
                try:
                    params = str(form.table.cleaned_data['name']) + "\n" \
                             + str(form.table.cleaned_data['comment']) + "\n" \
                             + str(form.table.cleaned_data['field_terminator']) + "\n" \
                             + str(form.table.cleaned_data['path']) + "\n" \
                             + str(form.table.cleaned_data['encoding']) + "\n" \
                             + str(form.table.cleaned_data['file_type']) + "\n" \
                             + str(form.table.cleaned_data['delimiter']) + "\n" \
                             + str(form.table.cleaned_data['read_column_headers']) + "\n" \
                             + str(form.table.cleaned_data['import_data']) + "\n" \
                             + str(form.table.cleaned_data['ignore_whitespaces']) + "\n" \
                             + str(form.table.cleaned_data['ignore_tabs']) + "\n" \
                             + str(form.table.cleaned_data['single_line_comment']) + "\n" \
                             + str(form.table.cleaned_data['java_style_comments']) + "\n" \
                             + str(form.table.cleaned_data['column_type']) + "\n" \
                             + str(form.table.cleaned_data['apply_excel_dialect'])
                    # return HttpResponse(str(params))

                    fields_list, n_cols, col_names, col_formset, columns = _delim_preview_ext(
                        file_type,
                        request.fs,
                        path,
                        None,
                        encoding,
                        [reader.TYPE for reader in FILE_READERS],
                        DELIMITERS,
                        True,
                        False)

                    preview_table_resp = django_mako.render_to_string("file_import_preview_table.mako", dict(
                            fields_list=fields_list,
                            column_formset=col_formset,
                    ))

                except Exception as ex:
                    preview_results['error'] = unicode(ex.message)
                else:
                    preview_results['results'] = preview_table_resp
                return HttpResponse(json.dumps(preview_results))
            if 'createTable' in request.POST:

                user_def_columns = []
                column_count = 0
                while 'cols-%d-column_name' % column_count in request.POST \
                    and 'cols-%d-column_type' % column_count in request.POST:
                    user_def_columns.append(dict(column_name=request.POST.get('cols-%d-column_name' % column_count),
                                        column_type=request.POST.get('cols-%d-column_type' % column_count), ))
                    column_count += 1

                delim = form.table.cleaned_data['delimiter']
                if not filter(lambda val: val[0] == delim, hcatalog.forms.TERMINATOR_CHOICES) and len(delim) > 0 and delim[0] != '\\':
                    delim = '\\' + delim
                table_name = form.table.cleaned_data['name']

                try:
                    fields_list, n_cols, col_names, col_formset, columns = _delim_preview_ext(
                        file_type,
                        request.fs,
                        path,
                        None,
                        encoding,
                        [reader.TYPE for reader in FILE_READERS],
                        DELIMITERS,
                        False,
                        True)

                    proposed_query = django_mako.render_to_string("create_table_templ_statement.mako",
                                                              {
                                                                  'table': dict(name=table_name,
                                                                                comment=form.table.cleaned_data['comment'],
                                                                                row_format='Delimited',
                                                                                field_terminator=delim),
                                                                  # 'columns': [f.cleaned_data for f in form.table.forms],
                                                                  'columns': user_def_columns,
                                                                  'partition_columns': []
                                                              }
                    )
                    proposed_query = proposed_query.replace('\\', '\\\\')
                    # do_load_data = s1_file_form.cleaned_data.get('do_import')
                    path = form.table.cleaned_data['path']
                    formatted_path = form.table.cleaned_data['formatted_path']
                    if formatted_path != '' and request.fs.exists(formatted_path):
                        if do_import_data:
                            request.fs.copyfile(formatted_path, path)
                            request.fs.remove(formatted_path)
                        else:
                            request.fs.remove(formatted_path)
                    return _submit_create_and_load(request, proposed_query, database, table_name, path, do_import_data)

                except Exception as ex:
                    return render("create_table_from_file.mako", request, dict(
                        action="#",
                        database=database,
                        table_form=form.table,
                        error=unicode(ex.message),
                    ))
    else:
        form.bind()
    return render("create_table_from_file.mako", request, dict(
            action="#",
            database=database,
            table_form=form.table,
            error=None,
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
                      ' ': 'spaces',
                      ';': 'semicolons'}
FILE_READERS = []


def _submit_create_and_load(request, create_hql, database, table_name, path, do_load):
    """
    Submit the table creation, and setup the load to happen (if ``do_load``).
    """
    # hcat_client().create_table(database, create_hql)
    hcat_client().create_table_by_templeton(database, table_name, create_hql )
    tables = _get_table_list(request)
    if do_load:
        if not table_name or not path:
            msg = 'Internal error: Missing needed parameter to load data into table'
            LOG.error(msg)
            raise Exception(msg)
        LOG.info("Auto loading data from %s into table %s" % (path, table_name))
        hql = "LOAD DATA INPATH '%s' INTO TABLE `%s`" % (path, table_name)
        hcatalog.views.do_load_table(request, hql)
    return render("show_tables.mako", request, dict(database=database, tables=tables, ))

def _delim_preview_ext(file_type, fs, path, path_tmp, encoding, file_types, delimiters, parse_first_row_as_header, apply_excel_dialect):

    if file_type == hcatalog.forms.IMPORT_FILE_TYPE_CSV_TSV:

        fields_list, n_cols, col_names = _delim_preview(fs, path, path_tmp, encoding, file_types, delimiters, parse_first_row_as_header, apply_excel_dialect)
        columns = []
        auto_column_types = HiveTypeAutoDefine().defineColumnTypes(fields_list[:100])
        if len(auto_column_types) == len(col_names):
            for i, col_name in enumerate(col_names):
                columns.append(dict(column_name=col_name, column_type=auto_column_types[i], ))
        else:
            for col_name in col_names:
                columns.append(dict(column_name=col_name, column_type='string', ))

        col_formset = hcatalog.forms.ColumnTypeFormSet(prefix='cols', initial=columns)

    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_XLS_XLSX:
        pass
    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_MS_ACCESS:
        pass

    return fields_list, n_cols, col_names, col_formset, columns

def _delim_preview(fs, path, path_tmp, encoding, file_types, delimiters, parse_first_row_as_header, apply_excel_dialect):
    if path_tmp is None:
        path_tmp = "/tmp/%s.tmp.%s" % (os.path.basename(path).replace(' ', ''), datetime.now().strftime("%s"))
    try:
        file_obj = fs.open(path)
        delim, file_type, fields_list = _parse_fields(
            fs, path, file_obj, encoding, file_types, delimiters, parse_first_row_as_header, apply_excel_dialect,
            path_tmp)
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

    # delim_form = hcatalog.forms.CreateByImportDelimForm(dict(delimiter_0=delimiter_0,
    #                                                          delimiter_1=delimiter_1,
    #                                                          file_type=file_type,
    #                                                          path_tmp=path_tmp,
    #                                                          n_cols=n_cols,
    #                                                          col_names=col_names,
    #                                                          parse_first_row_as_header=parse_first_row_as_header,
    #                                                          apply_excel_dialect=apply_excel_dialect))
    # if not delim_form.is_valid():
    #     assert False, _('Internal error when constructing the delimiter form: %(error)s' % {'error': delim_form.errors})
    return fields_list, n_cols, col_names##, delim_form


def unicode_csv_reader(encoding, unicode_csv_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(custom_csv_encoder(encoding, unicode_csv_data), dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, encoding) for cell in row]


def custom_csv_encoder(encoding, unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode(encoding)


def _parse_fields(fs, path, file_obj, encoding, filetypes, delimiters, parse_first_row_as_header, apply_excel_dialect,
                  path_tmp):
    """
    Go through the list of ``filetypes`` (gzip, text) and stop at the first one
    that works for the data. Then apply the list of ``delimiters`` and pick the
    most appropriate one.

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
                        csv_content = unicode_csv_reader(encoding, StringIO.StringIO('\n'.join(all_data)),
                                                         delimiter=delim.decode('string_escape'))
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
                        csvfile_tmp.write('\n'.join(all_data[1:]))
                    else:
                        csvfile_tmp.write('\n'.join(all_data))
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



HIVE_PRIMITIVE_TYPES = ("string", "tinyint", "smallint", "int", "bigint", "boolean", "float", "double")

HIVE_STRING_IDX = 0
HIVE_TINYINT_IDX = 1
HIVE_SMALLINT_IDX = 2
HIVE_INT_IDX = 3
HIVE_BIGINT_IDX = 4
HIVE_BOOLEAN_IDX = 5
HIVE_FLOAT_IDX = 6
HIVE_DOUBLE_IDX = 7
HIVE_PRIMITIVES_LEN = len(HIVE_PRIMITIVE_TYPES)


class HiveTypeAutoDefine(object):

    def isStrFloatingPointValue(self, strVal):
        return re.match(r'(^[+-]?((?:\d+\.\d+)|(?:\.\d+))(?:[eE][+-]?\d+)?$)', strVal) != None

    def isStrIntegerValue(self, strVal):
        return re.match(r'(^[+-]?\d+(?:[eE][+]?\d+)?$)', strVal) != None

    def isStrBooleanValue(self, strVal):
        return strVal == 'TRUE' or strVal == 'FALSE'

    def isIntHiveTinyint(self, intVal):
        return -2**7 <= intVal <= 2**7 - 1

    def isIntHiveSmallint(self, intVal):
        return -2**15 <= intVal <= 2**15 - 1

    def isIntHiveInt(self, intVal):
        return -2**31 <= intVal <= 2**31 - 1

    def isIntHiveBigint(self, intVal):
        return -2**63 <= intVal <= 2**63 - 1

    def defineFieldTypeIdx(self, strVal):
        if self.isStrFloatingPointValue(strVal):
            return HIVE_DOUBLE_IDX
        elif self.isStrIntegerValue(strVal):
            intVal = int(strVal)
            if self.isIntHiveTinyint(intVal):
                return HIVE_TINYINT_IDX
            elif self.isIntHiveSmallint(intVal):
                return HIVE_SMALLINT_IDX
            elif self.isIntHiveInt(intVal):
                return HIVE_INT_IDX
            elif self.isIntHiveBigint(intVal):
                return HIVE_BIGINT_IDX
        elif self.isStrBooleanValue(strVal):
            return HIVE_BOOLEAN_IDX
        return HIVE_STRING_IDX

    def defineFieldType(self, strVal):
        return HIVE_PRIMITIVE_TYPES[self.defineFieldTypeIdx(strVal)]

    def defineColumnTypes(self, matrix):
        column_types = []
        for row in matrix:
            if len(row) > len(column_types):
                for tmp in range(len(row) - len(column_types)):
                    column_types.append([0] * HIVE_PRIMITIVES_LEN)
            for i, field in enumerate(row):
                column_types[i][self.defineFieldTypeIdx(field)] += 1
        column_types = [ HIVE_PRIMITIVE_TYPES[types_list.index(max(types_list))] for types_list in column_types ]
        return column_types
