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
from desktop.lib.django_forms import MultiForm
from desktop.context_processors import get_app_name
from hadoop.fs import hadoopfs
from django.forms import ValidationError
from django.http import HttpResponse
from django.template.defaultfilters import escapejs


import hcatalog.common
import hcatalog.forms
from hcatalog.views import _get_table_list
from hcatalog.text_file_processing import GzipFileProcessor, TextFileProcessor
from hcat_client import hcat_client

import logging
import csv
import StringIO
from datetime import datetime
import os.path
import simplejson as json
import re


LOG = logging.getLogger(__name__)

FILE_PROCESSORS = []
FILE_PROCESSORS.append(GzipFileProcessor)
FILE_PROCESSORS.append(TextFileProcessor)


def create_from_file(request, database='default'):
    """Create a table by import from file"""
    form = MultiForm(
        table=hcatalog.forms.CreateTableFromFileForm,
    )
    if request.method == "POST":
        form.bind(request.POST)

        if form.is_valid():
            parser_options = {}
            table_name = form.table.cleaned_data['name']
            parser_options['field_terminator'] = form.table.cleaned_data['field_terminator']
            parser_options['do_import_data'] = form.table.cleaned_data['import_data']
            parser_options['path'] = form.table.cleaned_data['path']
            parser_options['encoding'] = form.table.cleaned_data['encoding']
            parser_options['file_type'] = form.table.cleaned_data['file_type']
            parser_options['autodetect_delimiter'] = form.table.cleaned_data['autodetect_delimiter']
            parser_options['read_column_headers'] = form.table.cleaned_data['read_column_headers']
            parser_options['apply_excel_dialect'] = True
            parser_options['ignore_whitespaces'] = form.table.cleaned_data['ignore_whitespaces']
            parser_options['ignore_tabs'] = form.table.cleaned_data['ignore_tabs']
            parser_options['single_line_comment'] = form.table.cleaned_data['single_line_comment']
            parser_options['java_style_comments'] = form.table.cleaned_data['java_style_comments']

            parser_options['formatted_path'] = None
            if 'table-formatted_path' in request.POST:
                parser_options['formatted_path'] = request.POST.get('table-formatted_path')
                if parser_options['formatted_path'] == '' or not request.fs.exists(parser_options['formatted_path']):
                    parser_options['formatted_path'] = None


            parser_options['field_terminator_cleaned'] = form.table.cleaned_data['field_terminator']
            if not filter(lambda val: val[0] == parser_options['field_terminator'], hcatalog.forms.TERMINATOR_CHOICES) and \
                    len(parser_options['field_terminator']) > 0 and parser_options['field_terminator'][0] != '\\':
                parser_options['field_terminator_cleaned'] = '\\' + parser_options['field_terminator_cleaned']

            if parser_options['autodetect_delimiter']:
                parser_options['delimiters'] = DELIMITERS
            else:
                parser_options['delimiter'] = (form.table.cleaned_data['delimiter'],)
                parser_options['delimiters'] = parser_options['delimiter']

            if 'submitPreviewAction' in request.POST: # preview action
                preview_results = {}
                preview_table_resp = ''
                fields_list, n_cols, col_names = ([], 0, [])
                try:
                    params = unicode(form.table.cleaned_data['name']) + "\n" \
                             + unicode(form.table.cleaned_data['comment']) + "\n" \
                             + unicode(form.table.cleaned_data['field_terminator']) + "\n" \
                             + unicode(form.table.cleaned_data['path']) + "\n" \
                             + unicode(form.table.cleaned_data['encoding']) + "\n" \
                             + unicode(form.table.cleaned_data['file_type']) + "\n" \
                             + unicode(form.table.cleaned_data['delimiter']) + "\n" \
                             + unicode(form.table.cleaned_data['autodetect_delimiter']) + "\n" \
                             + unicode(form.table.cleaned_data['read_column_headers']) + "\n" \
                             + unicode(form.table.cleaned_data['import_data']) + "\n" \
                             + unicode(form.table.cleaned_data['ignore_whitespaces']) + "\n" \
                             + unicode(form.table.cleaned_data['ignore_tabs']) + "\n" \
                             + unicode(form.table.cleaned_data['single_line_comment']) + "\n" \
                             + unicode(form.table.cleaned_data['java_style_comments']) + "\n" \
                             + unicode(form.table.cleaned_data['column_type']) + "\n" \
                             + unicode(form.table.cleaned_data['apply_excel_dialect'])


                    parser_options = _delim_preview_ext(request.fs, [processor.TYPE for processor in FILE_PROCESSORS], parser_options)

                    preview_table_resp = django_mako.render_to_string("file_import_preview_table.mako", dict(
                            fields_list=parser_options['fields_list'],
                            column_formset=parser_options['col_formset'],
                    ))

                except Exception as ex:
                    preview_results['error'] = escapejs(ex.message)
                else:
                    preview_results['results'] = preview_table_resp
                    options = {}

                    options["delimiter_0"] = parser_options['delimiter_0']
                    options["delimiter_1"] = parser_options['delimiter_1']
                    # options["field_terminator_0"] = parser_options['delimiter_0']
                    # options["field_terminator_1"] = parser_options['delimiter_1']
                    options["formatted_path"] = parser_options['formatted_path']

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
                    parser_options= _delim_preview_ext(request.fs, [processor.TYPE for processor in FILE_PROCESSORS], parser_options)


                    proposed_query = django_mako.render_to_string("create_table_templ_statement.mako",
                                                              {
                                                                  'table': dict(name=table_name,
                                                                                comment=form.table.cleaned_data['comment'],
                                                                                row_format='Delimited',
                                                                                field_terminator=parser_options['field_terminator_cleaned']),
                                                                  'columns': user_def_columns,
                                                                  'partition_columns': []
                                                              }
                    )
                    proposed_query = proposed_query.replace('\\', '\\\\')
                    path = form.table.cleaned_data['path']
                    if parser_options['formatted_path'] != '' and request.fs.exists(parser_options['formatted_path']):
                        if parser_options['do_import_data']:
                            request.fs.copyfile(parser_options['formatted_path'], parser_options['path'])
                            request.fs.remove(parser_options['formatted_path'])
                        else:
                            request.fs.remove(parser_options['formatted_path'])
                    return _submit_create_and_load(request, proposed_query, database, table_name, parser_options['path'], parser_options['do_import_data'])

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

def _delim_preview_ext(fs, file_types, parser_options):

    file_type = parser_options['file_type']
    if file_type == hcatalog.forms.IMPORT_FILE_TYPE_CSV_TSV:

        parser_options = _delim_preview(fs, file_types, parser_options)
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

    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_XLS_XLSX:
        pass
    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_MS_ACCESS:
        pass

    parser_options['col_formset'] = col_formset
    parser_options['columns'] = columns
    return parser_options


def _delim_preview(fs, file_types, parser_options):
    if parser_options['formatted_path'] is None:
        parser_options['formatted_path'] = "/tmp/%s.tmp.%s" % (os.path.basename(parser_options['path']).replace(' ', ''), datetime.now().strftime("%s"))
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


def unicode_csv_reader(encoding, unicode_csv_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(custom_csv_encoder(encoding, unicode_csv_data), dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, encoding) for cell in row]


def custom_csv_encoder(encoding, unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode(encoding)


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

            field_terminator_cleaned = parser_options['field_terminator_cleaned']
            # 'delimiter' is a MultiValueField. delimiter_0 and delimiter_1 are the sub-fields.
            delimiter_0 = delim
            delimiter_1 = ''
            delimiter_cleaned = delim
            # If custom delimiter
            if not filter(lambda val: val[0] == delim, hcatalog.forms.TERMINATOR_CHOICES):
                delimiter_0 = '__other__'
                delimiter_1 = delim
                if len(delim) > 0 and delim[0] != '\\':
                    delimiter_1 = '\\' + delim
                    delimiter_cleaned = '\\' + delim

            parser_options['delimiter_0'] = delimiter_0
            parser_options['delimiter_1'] = delimiter_1
            parser_options['delimiter_cleaned'] = delimiter_cleaned

            # creating tmp file to import data from
            if fs.exists(parser_options['formatted_path']):
                fs.remove(parser_options['formatted_path'])
            if parser_options['read_column_headers'] or parser_options['apply_excel_dialect']:
                try:
                    csvfile_tmp = fs.open(parser_options['formatted_path'], 'w')
                    file_obj.seek(0, hadoopfs.SEEK_SET)
                    all_data = processor.read_all_data(file_obj,
                                                       parser_options['encoding'],
                                                       ignore_whitespaces=parser_options['ignore_whitespaces'],
                                                       ignore_tabs=parser_options['ignore_tabs'],
                                                       single_line_comment=parser_options['single_line_comment'],
                                                       java_style_comments=parser_options['java_style_comments'])
                    if parser_options['apply_excel_dialect']:
                        csv_content = unicode_csv_reader(parser_options['encoding'], StringIO.StringIO('\n'.join(all_data)),
                                                         delimiter=delim.decode('string_escape'),)
                        new_fields_list = []
                        fields_list_start = 1 if parser_options['read_column_headers'] else 0
                        data_to_store = []
                        for row in csv_content:
                            new_row = []
                            for field in row:
                                new_row.append(field.replace(field_terminator_cleaned.decode('string_escape'), ''))
                            data_to_store.append(field_terminator_cleaned.decode('string_escape').join(new_row))
                            new_fields_list.append(new_row)
                        auto_column_types = HiveTypeAutoDefine().defineColumnTypes(new_fields_list[fields_list_start:IMPORT_COLUMN_AUTO_NLINES])
                        fields_list = new_fields_list[:IMPORT_PEEK_NLINES]
                    processor.write_all_data(csvfile_tmp, '\n'.join(data_to_store[fields_list_start:]), parser_options['encoding'])
                    csvfile_tmp.close()
                except IOError as ex:
                    msg = "Failed to open file '%s': %s" % (parser_options['path'], ex)
                    LOG.exception(msg)

            parser_options['processor_file_type'] = processor.TYPE
            parser_options['fields_list'] = fields_list
            parser_options['auto_column_types'] = auto_column_types
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
                if field:
                    column_types[i][self.defineFieldTypeIdx(field)] += 1
        column_types = [HIVE_PRIMITIVE_TYPES[HIVE_STRING_IDX]
                        if types_list[HIVE_STRING_IDX] > 0
                        else HIVE_PRIMITIVE_TYPES[types_list.index(max(types_list))]
                        for types_list in column_types]
        return column_types
