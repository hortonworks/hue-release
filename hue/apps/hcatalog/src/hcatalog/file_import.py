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


from desktop.lib import django_mako, i18n
from desktop.lib.django_util import render
from desktop.lib.django_forms import MultiForm
from desktop.context_processors import get_app_name
from hadoop.fs import hadoopfs
from django.http import HttpResponse
from django.template.defaultfilters import escapejs


import hcatalog.common
import hcatalog.forms
from hcatalog.views import _get_table_list
from hcatalog.file_processing import GzipFileProcessor, TextFileProcessor, XlsFileProcessor
from hcat_client import hcat_client

import logging
import csv
import StringIO
from datetime import datetime
import os.path
import simplejson as json
import re


LOG = logging.getLogger(__name__)

HCAT_HDFS_TMP_DIR = '/tmp/hcatalog'

FILE_PROCESSORS = []
FILE_PROCESSORS.append(GzipFileProcessor)
FILE_PROCESSORS.append(TextFileProcessor)

XLS_FILE_PROCESSOR = XlsFileProcessor()


def get_hcat_hdfs_tmp_dir(fs):
    if not fs.exists(HCAT_HDFS_TMP_DIR):
        fs.mkdir(HCAT_HDFS_TMP_DIR)
    return HCAT_HDFS_TMP_DIR


def get_xls_file_processor():
    return XLS_FILE_PROCESSOR


def create_from_file(request, database='default'):
    """Create a table by import from file"""
    form = MultiForm(
        table=hcatalog.forms.CreateTableFromFileForm,
    )
    if request.method == "POST":
        form.bind(request.POST)

        if form.is_valid():
            parser_options = {}

            # table options
            table_name = form.table.cleaned_data['name']
            field_terminator = form.table.cleaned_data['field_terminator']
            parser_options['field_terminator'] = field_terminator

            # common options
            parser_options['path'] = form.table.cleaned_data['path']
            file_type = form.table.cleaned_data['file_type']
            parser_options['file_type'] = form.table.cleaned_data['file_type']
            parser_options['preview_start_idx'] = 0
            parser_options['preview_end_idx'] = 0

            # csv/tsv options
            parser_options['do_import_data'] = form.table.cleaned_data['import_data']
            parser_options['encoding'] = form.table.cleaned_data['encoding']
            parser_options['autodetect_delimiter'] = form.table.cleaned_data['autodetect_delimiter']
            parser_options['read_column_headers'] = form.table.cleaned_data['read_column_headers']
            parser_options['apply_excel_dialect'] = True
            parser_options['ignore_whitespaces'] = form.table.cleaned_data['ignore_whitespaces']
            parser_options['ignore_tabs'] = form.table.cleaned_data['ignore_tabs']
            parser_options['single_line_comment'] = form.table.cleaned_data['single_line_comment']
            parser_options['java_style_comments'] = form.table.cleaned_data['java_style_comments']

            # xls/xlsx options
            parser_options['xls_sheet'] = form.table.cleaned_data['xls_sheet']
            parser_options['xls_cell_range'] = form.table.cleaned_data['xls_cell_range']
            parser_options['xls_read_column_headers'] = form.table.cleaned_data['xls_read_column_headers']


            parser_options['delimiter'] = form.table.cleaned_data['delimiter']
            if parser_options['autodetect_delimiter']:
                parser_options['delimiters'] = DELIMITERS
            else:
                parser_options['delimiters'] = parser_options['delimiter']

            if parser_options['xls_read_column_headers'] and parser_options['preview_start_idx'] == 0:
                parser_options['preview_start_idx'] = 1

            is_preview_action = 'submitPreviewAction' in request.POST
            is_preview_next = 'submitPreviewNext' in request.POST
            is_preview_beginning = 'submitPreviewBeginning' in request.POST
            if is_preview_action or is_preview_next or is_preview_beginning: # preview  action
                if is_preview_next and 'preview_start_idx' in request.POST and 'preview_end_idx' in request.POST:
                    parser_options['preview_start_idx'] = int(request.POST.get('preview_end_idx')) + 1
                    parser_options['preview_end_idx'] = int(request.POST.get('preview_end_idx')) + IMPORT_PEEK_NLINES
                else:
                    parser_options['preview_start_idx'] = 0
                    parser_options['preview_end_idx'] = IMPORT_PEEK_NLINES - 1
                if parser_options['xls_read_column_headers']:
                    parser_options['preview_start_idx'] += 1
                    parser_options['preview_end_idx'] += 1

                preview_results = {}
                preview_table_resp = ''
                fields_list, n_cols, col_names = ([], 0, [])
                try:
                    parser_options = _delim_preview_ext(request.fs, [processor.TYPE for processor in FILE_PROCESSORS], parser_options)
                    row_start_index = parser_options['preview_start_idx']
                    if parser_options['xls_read_column_headers']:
                        row_start_index -= 1
                    preview_table_resp = django_mako.render_to_string("file_import_preview_table.mako", dict(
                            fields_list=parser_options['fields_list'],
                            column_formset=parser_options['col_formset'],
                            row_start_index=row_start_index
                    ))

                except Exception as ex:
                    preview_results['error'] = escapejs(ex.message)
                else:
                    preview_results['results'] = preview_table_resp
                    options = {}

                    if file_type == hcatalog.forms.IMPORT_FILE_TYPE_CSV_TSV:
                        options["delimiter_0"] = parser_options['delimiter_0']
                        options["delimiter_1"] = parser_options['delimiter_1']
                    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_XLS_XLSX:
                        options["xls_sheet"] = parser_options['xls_sheet']
                        options["xls_sheet_list"] = parser_options['xls_sheet_list']
                        options["preview_start_idx"] = parser_options['preview_start_idx']
                        options["preview_end_idx"] = parser_options['preview_end_idx']
                        options["preview_has_more"] = parser_options['preview_has_more']

                    preview_results["options"] = options
                return HttpResponse(json.dumps(preview_results))
            else: # create table action
                user_def_columns = []
                column_count = 0
                while 'cols-%d-column_name' % column_count in request.POST \
                    and 'cols-%d-column_type' % column_count in request.POST:
                    user_def_columns.append(dict(column_name=request.POST.get('cols-%d-column_name' % column_count),
                                        column_type=request.POST.get('cols-%d-column_type' % column_count), ))
                    column_count += 1
                try:
                    parser_options['preview_and_create'] = True
                    parser_options = _delim_preview_ext(request.fs, [processor.TYPE for processor in FILE_PROCESSORS],
                                                        parser_options)

                    proposed_query = django_mako.render_to_string("create_table_statement.mako",
                                                                  {
                                                                      'table': dict(name=table_name,
                                                                                    comment=form.table.cleaned_data[
                                                                                        'comment'],
                                                                                    row_format='Delimited',
                                                                                    field_terminator=parser_options[
                                                                                        'field_terminator']),
                                                                      'columns': user_def_columns if user_def_columns else
                                                                      parser_options['columns'],
                                                                      'partition_columns': []
                                                                  })
                    proposed_query = proposed_query.decode('utf-8')
                    path = form.table.cleaned_data['path']
                    file_type = parser_options['file_type']

                    if file_type == hcatalog.forms.IMPORT_FILE_TYPE_XLS_XLSX:
                        path = parser_options['results_path']
                    else:
                        if parser_options['results_path'] != '' and request.fs.exists(parser_options['results_path']):
                            if parser_options['do_import_data']:
                                request.fs.copyfile(parser_options['results_path'], parser_options['path'])
                                request.fs.remove(parser_options['results_path'])
                            else:
                                request.fs.remove(parser_options['results_path'])
                    return _submit_create_and_load(request, proposed_query, database, table_name, path, parser_options['do_import_data'])

                except Exception as ex:
                    return render("create_table_from_file.mako", request, dict(
                        action="#",
                        database=database,
                        table_form=form.table,
                        error=escapejs(ex.message)
                    ))

            return render("create_table_from_file.mako", request, dict(
                action="#",
                database=database,
                table_form=form.table,
                error="User form is not valid. Please check all input parameters.",
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
IMPORT_COLUMN_AUTO_NLINES = 200
DELIMITERS = [hive_val for hive_val, _, _ in hcatalog.common.TERMINATORS]
DELIMITER_READABLE = {'\\001': 'ctrl-As',
                      '\\002': 'ctrl-Bs',
                      '\\003': 'ctrl-Cs',
                      '\\t': 'tabs',
                      ',': 'commas',
                      ' ': 'spaces',
                      ';': 'semicolons'}


def _submit_create_and_load(request, create_hql, database, table_name, path, do_load):
    """
    Submit the table creation, and setup the load to happen (if ``do_load``).
    """
    hcat_client().create_table_by_templeton(database, table_name, create_hql)
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

def _delim_preview_ext(fs, file_types, parser_options):
    file_type = parser_options['file_type']
    if file_type == hcatalog.forms.IMPORT_FILE_TYPE_CSV_TSV:
        parser_options = _text_file_preview(fs, file_types, parser_options)
    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_XLS_XLSX:
        parser_options = _xls_file_preview(fs, parser_options)
    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_MS_ACCESS:
        pass

    auto_column_types = parser_options['auto_column_types'] if 'auto_column_types' in parser_options else []
    col_names = parser_options['col_names'] if 'col_names' in parser_options else []
    columns = []
    if len(auto_column_types) == len(col_names):
        for i, col_name in enumerate(col_names):
            columns.append(dict(column_name=col_name, column_type=auto_column_types[i], ))
    else:
        for col_name in col_names:
            columns.append(dict(column_name=col_name, column_type='string', ))
    col_formset = hcatalog.forms.ColumnTypeFormSet(prefix='cols', initial=columns)
    parser_options['col_formset'] = col_formset
    parser_options['columns'] = columns
    return parser_options


def _text_file_preview(fs, file_types, parser_options):
    results_file_name = None
    preview_and_create = 'preview_and_create' in parser_options
    if preview_and_create:
        results_file_name = get_hcat_hdfs_tmp_dir(fs) + "/%s.tmp.%s" % \
                    (os.path.basename(parser_options['path']).replace(' ', ''), datetime.now().strftime("%s"))
        parser_options['results_path'] = results_file_name

    try:
        file_obj = fs.open(parser_options['path'])
        parser_options = _parse_fields(fs, file_obj, file_types, parser_options)
        file_obj.close()
    except IOError as ex:
        msg = "Failed to open file '%s': %s" % (parser_options['path'], ex)
        LOG.exception(msg)
        raise Exception(msg)
    except Exception as ex:
        raise Exception('Delimiter preview error: %s' % unicode(ex))

    col_names = []
    fields_list = parser_options['fields_list']
    n_cols = max([len(row) for row in fields_list])

    # making column list and preview data part
    if parser_options['read_column_headers'] and len(fields_list) > 0:
        col_names = fields_list[0]
        fields_list = fields_list[1:IMPORT_PEEK_NLINES]
        if len(col_names) < n_cols:
            for i in range(len(col_names) + 1, n_cols + 1):
                col_names.append('col_%s' % (i,))
    elif not parser_options['read_column_headers']:
        for i in range(1, n_cols + 1):
            col_names.append('col_%s' % (i,))

    parser_options['fields_list'] = fields_list
    parser_options['n_cols'] = n_cols
    parser_options['col_names'] = col_names
    return parser_options


def _xls_file_preview(fs, parser_options):
    preview_and_create = 'preview_and_create' in parser_options
    if preview_and_create:
        file_name = get_hcat_hdfs_tmp_dir(fs) + '/%s' % \
                    (os.path.splitext(os.path.basename(parser_options['path'].replace(' ', '')))[0] + '.dsv.gz')
        parser_options['results_path'] = file_name
        result_file_obj = fs.open(file_name, 'w')
    try:
        file_obj = fs.open(parser_options['path'])
        xls_sheet_selected = parser_options['xls_sheet']

        xls_fileobj = get_xls_file_processor().open(file_obj)
        sheets = [[str(idx), name] for idx, name in enumerate(get_xls_file_processor().get_sheet_list(xls_fileobj))]
        if not xls_sheet_selected in [sh[0] for sh in sheets]:
            xls_sheet_selected = '0'

        xls_read_column_headers = parser_options['xls_read_column_headers']
        xls_cell_range = parser_options['xls_cell_range']
        col_names = []
        if xls_read_column_headers:
            fields_list = get_xls_file_processor().get_scope_data(xls_fileobj, xls_sheet_selected,
                                                               cell_range=xls_cell_range,
                                                               row_start_idx=0,
                                                               row_end_idx=0)
            if len(fields_list) == 1:
                col_names = fields_list[0]
        else:
            col_names = get_xls_file_processor().get_column_names(xls_fileobj, int(xls_sheet_selected),
                                                               cell_range=xls_cell_range)

        row_start_idx = parser_options['preview_start_idx']
        row_end_idx = parser_options['preview_end_idx'] + 1  # read one more row over to define has_more flag

        if preview_and_create:
            fields_list = get_xls_file_processor().get_scope_data(xls_fileobj, xls_sheet_selected,
                                                               cell_range=xls_cell_range)
        else:
            fields_list = get_xls_file_processor().get_scope_data(xls_fileobj, xls_sheet_selected,
                                                           cell_range=xls_cell_range,
                                                           row_start_idx=row_start_idx,
                                                           row_end_idx=row_end_idx)

        preview_has_more = row_end_idx - row_start_idx == len(fields_list) - 1
        if preview_has_more:
            fields_list = fields_list[:-1]
            row_end_idx -= 1

        if preview_and_create:
            fields_list_start = 1 if parser_options['xls_read_column_headers'] else 0
            fields_list = fields_list[fields_list_start:]
            get_xls_file_processor().write_to_dsv_gzip(xls_fileobj, result_file_obj, fields_list, parser_options['field_terminator'])
            result_file_obj.close()

        file_obj.close()

        auto_column_types = HiveTypeAutoDefine().defineColumnTypes(fields_list[:IMPORT_COLUMN_AUTO_NLINES])

    except IOError as ex:
        msg = "Failed to open file '%s': %s" % (parser_options['path'], ex)
        LOG.exception(msg)
        raise Exception(msg)
    except Exception as ex:
        raise Exception('Delimiter preview error: %s' % unicode(ex))

    parser_options['xls_sheet'] = xls_sheet_selected
    parser_options['xls_sheet_list'] = sheets
    parser_options['fields_list'] = fields_list
    parser_options['preview_start_idx'] = row_start_idx
    parser_options['preview_end_idx'] = row_end_idx
    parser_options['preview_has_more'] = preview_has_more
    parser_options['n_cols'] = len(col_names)
    parser_options['col_names'] = col_names
    parser_options['auto_column_types'] = auto_column_types
    return parser_options


def unicode_csv_reader(encoding, unicode_csv_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(custom_csv_encoder(encoding, unicode_csv_data), dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, encoding) for cell in row]


def custom_csv_encoder(encoding, unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode(encoding)


def _text_file_convert(fs, src_file_obj, processor, parser_options):

    if fs.exists(parser_options['results_path']):
        fs.remove(parser_options['results_path'])
    if parser_options['read_column_headers'] or parser_options['apply_excel_dialect']:
        try:
            csvfile_tmp = fs.open(parser_options['results_path'], 'w')
            src_file_obj.seek(0, hadoopfs.SEEK_SET)
            all_data = processor.read_all_data(src_file_obj,
                                               parser_options['encoding'],
                                               ignore_whitespaces=parser_options['ignore_whitespaces'],
                                               ignore_tabs=parser_options['ignore_tabs'],
                                               single_line_comment=parser_options['single_line_comment'],
                                               java_style_comments=parser_options['java_style_comments'])
            if parser_options['apply_excel_dialect']:
                csv_content = unicode_csv_reader(parser_options['encoding'], StringIO.StringIO('\n'.join(all_data)),
                                                 delimiter=parser_options['delimiter'].decode('string_escape'),)
                new_fields_list = []
                fields_list_start = 1 if parser_options['read_column_headers'] else 0
                data_to_store = []
                for row_idx, row in enumerate(csv_content):
                    new_row = []
                    for field in row:
                        new_row.append(field.replace(parser_options['field_terminator'].decode('string_escape'), ''))
                    data_to_store.append(parser_options['field_terminator'].decode('string_escape').join(new_row))
                    if row_idx <= IMPORT_COLUMN_AUTO_NLINES:
                        new_fields_list.append(new_row)
                auto_column_types = HiveTypeAutoDefine().defineColumnTypes(new_fields_list[fields_list_start:IMPORT_COLUMN_AUTO_NLINES])
                fields_list = new_fields_list[:IMPORT_PEEK_NLINES]
                parser_options['fields_list'] = fields_list
                parser_options['auto_column_types'] = auto_column_types
            processor.write_all_data(csvfile_tmp, '\n'.join(data_to_store[fields_list_start:]), parser_options['encoding'])
            csvfile_tmp.close()
        except IOError as ex:
            msg = "Failed to open file '%s': %s" % (parser_options['path'], ex)
            LOG.exception(msg)


def _text_preview_convert(lines, parser_options):

    if parser_options['read_column_headers'] or parser_options['apply_excel_dialect']:
        if parser_options['apply_excel_dialect']:
            csv_content = unicode_csv_reader(parser_options['encoding'], StringIO.StringIO('\n'.join(lines)),
                                             delimiter=parser_options['delimiter'].decode('string_escape'),)
            new_fields_list = []
            fields_list_start = 1 if parser_options['read_column_headers'] else 0
            for row in csv_content:
                new_row = []
                for field in row:
                    new_row.append(field.replace(parser_options['field_terminator'].decode('string_escape'), ''))
                new_fields_list.append(new_row)
            auto_column_types = HiveTypeAutoDefine().defineColumnTypes(new_fields_list[fields_list_start:IMPORT_COLUMN_AUTO_NLINES])
            fields_list = new_fields_list[:IMPORT_PEEK_NLINES]
            parser_options['fields_list'] = fields_list
            parser_options['auto_column_types'] = auto_column_types


def _parse_fields(fs, file_obj, filetypes, parser_options):
    """
    Go through the list of 'filetypes' (gzip, text) and stop at the first one
    that works for the data. Then apply the list of 'delimiters' and pick the
    most appropriate one.

    Return the best delimiter, filetype and the data broken down into rows of fields.
    """
    file_processors = [processor for processor in FILE_PROCESSORS if processor.TYPE in filetypes]

    for processor in file_processors:
        LOG.debug("Trying %s for file: %s" % (processor.TYPE, parser_options['path']))
        file_obj.seek(0, hadoopfs.SEEK_SET)
        lines = processor.readlines(file_obj, parser_options['encoding'],
                                    ignore_whitespaces=parser_options['ignore_whitespaces'],
                                    ignore_tabs=parser_options['ignore_tabs'],
                                    single_line_comment=parser_options['single_line_comment'],
                                    java_style_comments=parser_options['java_style_comments'])
        auto_column_types = []
        if lines is not None:
            delim, fields_list = _readfields(lines, parser_options['delimiters'])

            # 'delimiter' is a MultiValueField. delimiter_0 and delimiter_1 are the sub-fields.
            delimiter_0 = delim
            delimiter_1 = ''
            # If custom delimiter
            if not filter(lambda val: val[0] == delim, hcatalog.forms.TERMINATOR_CHOICES):
                delimiter_0 = '__other__'
                delimiter_1 = delim

            parser_options['delimiter_0'] = delimiter_0
            parser_options['delimiter_1'] = delimiter_1
            parser_options['delimiter'] = delim

            preview_and_create = 'preview_and_create' in parser_options
            if preview_and_create:
                _text_file_convert(fs, file_obj, processor, parser_options)
            else:
                _text_preview_convert(lines, parser_options)

            parser_options['processor_file_type'] = processor.TYPE
            # parser_options['fields_list'] = fields_list
            # parser_options['auto_column_types'] = auto_column_types
            return parser_options
    else:
        # Even TextFileReader doesn't work
        msg = "Failed to decode file '%s' into printable characters under %s" % (parser_options['path'], parser_options['encoding'],)
        LOG.error(msg)
        raise Exception(msg)


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

    def defineFieldTypeIdx(self, strVal, min_int_type=HIVE_TINYINT_IDX):
        if self.isStrIntegerValue(strVal):
            intVal = int(strVal)
            if HIVE_TINYINT_IDX >= min_int_type and self.isIntHiveTinyint(intVal):
                return HIVE_TINYINT_IDX
            elif HIVE_SMALLINT_IDX >= min_int_type and self.isIntHiveSmallint(intVal):
                return HIVE_SMALLINT_IDX
            elif HIVE_INT_IDX >= min_int_type and self.isIntHiveInt(intVal):
                return HIVE_INT_IDX
            elif HIVE_BIGINT_IDX >= min_int_type and self.isIntHiveBigint(intVal):
                return HIVE_BIGINT_IDX
        elif self.isStrFloatingPointValue(strVal):
            return HIVE_DOUBLE_IDX
        elif self.isStrBooleanValue(strVal):
            return HIVE_BOOLEAN_IDX
        return HIVE_STRING_IDX

    def defineFieldType(self, strVal):
        return HIVE_PRIMITIVE_TYPES[self.defineFieldTypeIdx(strVal)]

    def defineColumnTypes(self, matrix, min_int_type=HIVE_INT_IDX):
        column_types = []
        for row in matrix:
            if len(row) > len(column_types):
                for tmp in range(len(row) - len(column_types)):
                    column_types.append([0] * HIVE_PRIMITIVES_LEN)
            for i, field in enumerate(row):
                if field:
                    column_types[i][self.defineFieldTypeIdx(str(field), min_int_type=min_int_type)] += 1
        column_types = [HIVE_PRIMITIVE_TYPES[HIVE_STRING_IDX]
                        if types_list[HIVE_STRING_IDX] > 0
                        else HIVE_PRIMITIVE_TYPES[types_list.index(max(types_list))]
                        for types_list in column_types]
        return column_types
