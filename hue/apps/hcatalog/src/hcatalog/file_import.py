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
from desktop.lib.json_utils import JSONEncoderForHTML
from hadoop.fs import hadoopfs
from django.core import urlresolvers
from django.http import HttpResponse
from django.template.defaultfilters import escapejs


import hcatalog.common
import hcatalog.forms
from hcatalog.views import _get_table_list, _get_last_database
from hcatalog.file_processing import GzipFileProcessor, TextFileProcessor, XlsFileProcessor, CommentsDetector
from hcat_client import HCatClient
from beeswax.server import dbms

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
        fs.do_as_superuser(fs.mkdir, HCAT_HDFS_TMP_DIR)
        fs.do_as_superuser(fs.chmod, HCAT_HDFS_TMP_DIR, 0777)
    return HCAT_HDFS_TMP_DIR


def get_xls_file_processor():
    return XLS_FILE_PROCESSOR


def create_from_file(request, database=None):
    """Create a table by import from file"""
    if database is None:
        database = _get_last_database(request)
    form = MultiForm(
        table=hcatalog.forms.CreateTableFromFileForm,
    )
    db = dbms.get(request.user)
    databases = db.get_databases()
    db_form = hcatalog.forms.DbForm(initial={'database': database}, databases=databases)

    if request.method == "POST":
        form.bind(request.POST)

        if form.is_valid():
            parser_options = {}

            # table options
            table_name = form.table.cleaned_data['name']
            replace_delimiter_with = form.table.cleaned_data['replace_delimiter_with']
            parser_options['replace_delimiter_with'] = replace_delimiter_with

            # common options
            parser_options['path'] = form.table.cleaned_data['path']
            file_type = request.POST.get('file_type', hcatalog.forms.IMPORT_FILE_TYPE_NONE)
            parser_options['file_type'] = file_type
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
                parser_options['delimiters'] = (parser_options['delimiter'],)

            if parser_options['xls_read_column_headers'] and parser_options['preview_start_idx'] == 0:
                parser_options['preview_start_idx'] = 1

            is_preview_action = 'submitPreviewAction' in request.POST
            is_preview_next = 'submitPreviewNext' in request.POST
            is_preview_beginning = 'submitPreviewBeginning' in request.POST
            if is_preview_action or is_preview_next or is_preview_beginning:  # preview  action
                preview_results = {}
                preview_table_resp = ''
                fields_list, n_cols, col_names = ([], 0, [])

                # validate input parameters
                if file_type == hcatalog.forms.IMPORT_FILE_TYPE_NONE:
                    preview_results['error'] = unicode('Cannot define file type.')
                    return HttpResponse(json.dumps(preview_results))

                if is_preview_next and 'preview_start_idx' in request.POST and 'preview_end_idx' in request.POST:
                    parser_options['preview_start_idx'] = int(request.POST.get('preview_end_idx')) + 1
                    parser_options['preview_end_idx'] = int(request.POST.get('preview_end_idx')) + IMPORT_PEEK_NLINES
                else:
                    parser_options['preview_start_idx'] = 0
                    parser_options['preview_end_idx'] = IMPORT_PEEK_NLINES - 1
                if parser_options['xls_read_column_headers']:
                    parser_options['preview_start_idx'] += 1
                    parser_options['preview_end_idx'] += 1

                try:
                    parser_options = _on_table_preview(request.fs, [processor.TYPE for processor in FILE_PROCESSORS],
                                                        parser_options)
                    row_start_index = parser_options['preview_start_idx']
                    if parser_options['xls_read_column_headers']:
                        row_start_index -= 1
                    preview_table_resp = django_mako.render_to_string("file_import_preview_table.mako", dict(
                        fields_list=parser_options['fields_list'],
                        column_formset=parser_options['col_formset'],
                        row_start_index=row_start_index
                    ))
                    isTableValid, tableValidErrMsg = hcatalog.common.validateHiveTable(parser_options['col_names'])
                except Exception as ex:
                    preview_results['error'] = escapejs(ex.message)
                else:
                    preview_results['results'] = preview_table_resp
                    if not isTableValid:
                        preview_results['error'] = escapejs(tableValidErrMsg)
                    options = {}
                    if file_type == hcatalog.forms.IMPORT_FILE_TYPE_TEXT:
                        options['delimiter_0'] = parser_options['delimiter_0']
                        options['delimiter_1'] = parser_options['delimiter_1']
                        options['file_processor_type'] = parser_options['file_processor_type']
                    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_SPREADSHEET:
                        options['xls_sheet'] = parser_options['xls_sheet']
                        options['xls_sheet_list'] = parser_options['xls_sheet_list']
                        options['preview_start_idx'] = parser_options['preview_start_idx']
                        options['preview_end_idx'] = parser_options['preview_end_idx']
                        options['preview_has_more'] = parser_options['preview_has_more']

                    preview_results['options'] = options
                return HttpResponse(json.dumps(preview_results, cls=JSONEncoderForHTML))
            else:  # create table action
                # validate input parameters
                if file_type == hcatalog.forms.IMPORT_FILE_TYPE_NONE:
                    err_msg = unicode('Cannot define file type.')
                    return render("create_table_from_file.mako", request, dict(
                        action="#",
                        database=database,
                        db_form=db_form,
                        table_form=form.table,
                        error=err_msg)
                    )
                # getting back file_processor_type from preview
                parser_options['file_processor_type'] = request.POST.get('file_processor_type', None)
                user_def_columns = []
                user_def_column_names = []
                column_count = 0
                while 'cols-%d-column_name' % column_count in request.POST \
                    and 'cols-%d-column_type' % column_count in request.POST:
                    user_def_column_names.append(request.POST.get('cols-%d-column_name' % column_count))
                    user_def_columns.append(dict(column_name=request.POST.get('cols-%d-column_name' % column_count),
                                        column_type=request.POST.get('cols-%d-column_type' % column_count), ))
                    column_count += 1
                try:
                    isTableValid, tableValidErrMsg = hcatalog.common.validateHiveTable(user_def_column_names)
                    if not isTableValid:
                        return render("create_table_from_file.mako", request, dict(
                            action="#",
                            database=database,
                            db_form=db_form,
                            table_form=form.table,
                            error=escapejs(tableValidErrMsg)
                        ))

                    LOG.debug('Creating table by hcatalog')
                    proposed_query = django_mako.render_to_string("create_table_statement.mako",
                                                                  {
                                                                      'table': dict(name=table_name,
                                                                                    comment=form.table.cleaned_data[
                                                                                        'comment'],
                                                                                    row_format='Delimited',
                                                                                    field_terminator=replace_delimiter_with),
                                                                      'columns': user_def_columns,
                                                                      'partition_columns': []
                                                                  })
                    proposed_query = proposed_query.decode('utf-8')
                    hcat_cli = HCatClient(request.user.username)
                    hcat_cli.create_table(database, table_name, proposed_query)

                    do_import_data = parser_options.get('do_import_data', True)
                    LOG.debug('Data processing stage')
                    if do_import_data:
                        parser_options = _on_table_create(request.fs, parser_options)
                        path = parser_options.get('results_path', None)
                        if not path or not request.fs.exists(path):
                            msg = 'Missing needed result file to load data into table'
                            LOG.error(msg)
                            raise Exception(msg)
                        if not table_name:
                            msg = 'Internal error: Missing needed parameter to load data into table'
                            LOG.error(msg)
                            raise Exception(msg)
                        LOG.info("Auto loading data from %s into table %s%s" % (path, database, table_name))
                        hql = "LOAD DATA INPATH '%s' INTO TABLE `%s.%s`" % (path, database, table_name)
                        job_id = hcat_cli.do_hive_query(execute=hql)
                        on_success_url = urlresolvers.reverse(get_app_name(request) + ':index')
                        return render("create_table_from_file.mako", request, dict(
                            action="#",
                            job_id=job_id,
                            on_success_url=on_success_url,
                            database=database,
                            db_form=db_form,
                            table_form=form.table,
                            error=None,
                        ))

                    # clean up tmp dir
                    tmp_dir = parser_options.get('tmp_dir', None)
                    if tmp_dir and request.fs.exists:
                        request.fs.rmtree(tmp_dir)

                    databases = hcat_cli.get_databases(like="*")
                    db_form = hcatalog.forms.DbForm(initial={'database': database}, databases=databases)
                    return render("show_tables.mako", request, {
                        'database': database,
                        'db_form': db_form,
                    })

                except Exception as ex:
                    return render("create_table_from_file.mako", request, dict(
                        action="#",
                        database=database,
                        db_form=db_form,
                        table_form=form.table,
                        error=escapejs(ex.message)
                    ))

        return render("create_table_from_file.mako", request, dict(
            action="#",
            database=database,
            db_form=db_form,
            table_form=form.table,
            error="User form is not valid. Please check all input parameters.",
        ))
    else:
        form.bind()
    return render("create_table_from_file.mako", request, dict(
            action="#",
            database=database,
            db_form=db_form,
            table_form=form.table,
            error=None,
    ))


IMPORT_PEEK_SIZE = 8192
IMPORT_MAX_SIZE = 4294967296  # 4 Gb
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


def _on_table_preview(fs, file_types, parser_options):
    file_type = parser_options['file_type']
    if file_type == hcatalog.forms.IMPORT_FILE_TYPE_TEXT:
        parser_options = _text_file_preview(fs, file_types, parser_options)
    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_SPREADSHEET:
        parser_options = _xls_file_preview(fs, parser_options)
    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_MS_ACCESS:
        pass

    auto_column_types = parser_options['auto_column_types'] if 'auto_column_types' in parser_options else []
    col_names = parser_options['col_names'] if 'col_names' in parser_options else []
    col_names = make_up_hive_column_names(col_names)
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
    parser_options['col_names'] = col_names
    return parser_options


def _on_table_create(fs, parser_options):
    file_type = parser_options['file_type']
    if file_type == hcatalog.forms.IMPORT_FILE_TYPE_TEXT:
        parser_options = _text_file_create(fs, parser_options)
    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_SPREADSHEET:
        parser_options = _xls_file_create(fs, parser_options)
    elif file_type == hcatalog.forms.IMPORT_FILE_TYPE_MS_ACCESS:
        pass
    return parser_options


def make_up_hive_column_names(names):
    new_names = []
    for col_name in names:
        col_name = re.sub(r'[^a-zA-Z0-9]+', '_', unicode(col_name).lower())
        if not col_name:
            new_names.append('')
            continue
        col_rename_idx = 0
        while (col_name + '_' + str(col_rename_idx) if col_rename_idx else col_name) in new_names:
            col_rename_idx += 1
        else:
            new_names.append(col_name + '_' + str(col_rename_idx) if col_rename_idx else col_name)
    return new_names

def _text_file_preview(fs, file_types, parser_options):
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


def _text_file_create(fs, parser_options):
    hcat_tmp_dir = get_hcat_hdfs_tmp_dir(fs) + '/%s' % (datetime.now().strftime("%s"))
    fs.mkdir(hcat_tmp_dir)
    fs.do_as_superuser(fs.chmod, hcat_tmp_dir, 0777)
    results_path = hcat_tmp_dir + '/%s' % (os.path.basename(parser_options['path']).replace(' ', ''))
    parser_options['tmp_dir'] = hcat_tmp_dir
    parser_options['results_path'] = results_path
    file_processor_type = parser_options.get('file_processor_type', None)
    processor = None
    for p in FILE_PROCESSORS:
        if p.TYPE == file_processor_type:
            processor = p
            break
    else:
        raise Exception('Could not determine file processor type')
    parser_options = _text_file_convert(fs, processor, parser_options)
    return parser_options

def _xls_file_preview(fs, parser_options):
    try:
        file_obj = fs.open(parser_options['path'])
        xls_sheet_selected = parser_options['xls_sheet']

        xls_fileobj = get_xls_file_processor().open(file_obj)
        sheets = [[unicode(idx), name] for idx, name in enumerate(get_xls_file_processor().get_sheet_list(xls_fileobj))]
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
        fields_list = get_xls_file_processor().get_scope_data(xls_fileobj, xls_sheet_selected,
                                                              cell_range=xls_cell_range,
                                                              row_start_idx=row_start_idx,
                                                              row_end_idx=row_end_idx)

        preview_has_more = row_end_idx - row_start_idx == len(fields_list) - 1
        if preview_has_more:
            fields_list = fields_list[:-1]
            row_end_idx -= 1
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


def _xls_file_create(fs, parser_options):
    hcat_tmp_dir = get_hcat_hdfs_tmp_dir(fs) + '/%s' % (datetime.now().strftime("%s"))
    fs.mkdir(hcat_tmp_dir)
    results_path = hcat_tmp_dir + '/%s' % (os.path.splitext(os.path.basename(parser_options['path'].replace(' ', '')))[0] + '.dsv.gz')
    parser_options['tmp_dir'] = hcat_tmp_dir
    parser_options['results_path'] = results_path
    fs.create(results_path, overwrite=True, permission=0777)
    file_obj = fs.open(parser_options['path'])
    xls_sheet_selected = parser_options['xls_sheet']

    xls_fileobj = get_xls_file_processor().open(file_obj)
    sheets = [[unicode(idx), name] for idx, name in enumerate(get_xls_file_processor().get_sheet_list(xls_fileobj))]
    if not xls_sheet_selected in [sh[0] for sh in sheets]:
        xls_sheet_selected = '0'

    xls_read_column_headers = parser_options['xls_read_column_headers']
    xls_cell_range = parser_options['xls_cell_range']
    fields_list = get_xls_file_processor().get_scope_data(xls_fileobj, xls_sheet_selected, cell_range=xls_cell_range)
    fields_list_start = 1 if xls_read_column_headers else 0
    fields_list = fields_list[fields_list_start:]
    get_xls_file_processor().write_to_dsv_gzip(fs, xls_fileobj, results_path, fields_list,
                                               parser_options['replace_delimiter_with'])
    return parser_options


def unicode_csv_reader(encoding, unicode_csv_data, cell_delim_to_skip=None, cell_skip_lfs=False, join_cells_with=None,
                       dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(custom_csv_encoder(encoding, unicode_csv_data), dialect=dialect, **kwargs)
    if join_cells_with:
        if cell_delim_to_skip and cell_skip_lfs:
            for row in csv_reader:
                yield join_cells_with.join([unicode(cell, encoding).replace('\r', '').replace('\n', '').replace(cell_delim_to_skip, '') for cell in row])
        elif cell_skip_lfs:
            for row in csv_reader:
                yield join_cells_with.join([unicode(cell, encoding).replace('\r', '').replace('\n', '') for cell in row])
        elif cell_delim_to_skip:
            for row in csv_reader:
                yield join_cells_with.join([unicode(cell, encoding).replace(cell_delim_to_skip, '') for cell in row])
        else:
            for row in csv_reader:
                yield join_cells_with.join([unicode(cell, encoding) for cell in row])
    else:
        if cell_delim_to_skip and cell_skip_lfs:
            for row in csv_reader:
                yield [unicode(cell, encoding).replace('\r', '').replace('\n', '').replace(cell_delim_to_skip, '') for cell in row]
        elif cell_skip_lfs:
            for row in csv_reader:
                yield [unicode(cell, encoding).replace('\r', '').replace('\n', '') for cell in row]
        elif cell_delim_to_skip:
            for row in csv_reader:
                yield [unicode(cell, encoding).replace(cell_delim_to_skip, '') for cell in row]
        else:
            for row in csv_reader:
                yield [unicode(cell, encoding) for cell in row]


def custom_csv_encoder(encoding, unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode(encoding)


def _text_file_convert(fs, processor, parser_options):
    results_path = parser_options['results_path']
    fs.create(results_path, overwrite=True, permission=0777)
    encoding = parser_options['encoding']
    path = parser_options['path']
    ignore_whitespaces = parser_options.get('ignore_whitespaces', False)
    ignore_tabs = parser_options.get('ignore_tabs', False)
    single_line_comment = parser_options.get('single_line_comment', None)
    java_style_comments = parser_options.get('java_style_comments', False)
    delimiter_decoded = parser_options['delimiter'].decode('string_escape')
    replace_delimiter_with_decoded = parser_options['replace_delimiter_with'].decode('string_escape')

    if java_style_comments or single_line_comment:
        comment_detector = CommentsDetector(java_line_comment=java_style_comments,
                                            java_block_comment=java_style_comments,
                                            custom_line_comment=single_line_comment)
    first_chunk = True
    chunk_offset = 0
    for chunk in processor.read_in_chunks(fs, path, encoding):
        # skipping comments at first
        if java_style_comments or single_line_comment:
            chunk = comment_detector.skip_comments(chunk, index_offset=chunk_offset)
            chunk_offset += len(chunk)
        if ignore_whitespaces:
            chunk = chunk.replace(' ', '')
        if ignore_tabs:
            chunk = chunk.replace('\t', '')
        data_to_store = unicode_csv_reader(encoding, StringIO.StringIO(chunk), delimiter=delimiter_decoded,
                                           cell_delim_to_skip=replace_delimiter_with_decoded, cell_skip_lfs=True,
                                           join_cells_with=replace_delimiter_with_decoded)
        data_to_store = [row for row in data_to_store]
        if first_chunk:
            fields_list_start = 1 if parser_options['read_column_headers'] else 0
            processor.append_chunk(fs, results_path, '\n'.join(data_to_store[fields_list_start:]), encoding)
            first_chunk = False
        else:
            processor.append_chunk(fs, results_path, '\n' + '\n'.join(data_to_store), encoding)

    return parser_options


def _text_preview_convert(lines, parser_options):

    if parser_options['read_column_headers'] or parser_options['apply_excel_dialect']:
        if parser_options['apply_excel_dialect']:
            delimiter_decoded = parser_options['delimiter'].decode('string_escape')
            replace_delimiter_with_decoded = parser_options['replace_delimiter_with'].decode('string_escape')
            new_fields_list = unicode_csv_reader(parser_options['encoding'], StringIO.StringIO('\n'.join(lines)),
                                             delimiter=delimiter_decoded,
                                             cell_delim_to_skip=replace_delimiter_with_decoded, cell_skip_lfs=True)
            fields_list_start = 1 if parser_options['read_column_headers'] else 0
            new_fields_list = [row for row in new_fields_list]
            auto_column_types = HiveTypeAutoDefine().defineColumnTypes(new_fields_list[fields_list_start:IMPORT_COLUMN_AUTO_NLINES])
            fields_list = new_fields_list[:IMPORT_PEEK_NLINES]
            parser_options['fields_list'] = fields_list
            parser_options['auto_column_types'] = auto_column_types
    return parser_options


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
        lines = processor.read_preview_lines(file_obj, parser_options['encoding'],
                                    ignore_whitespaces=parser_options['ignore_whitespaces'],
                                    ignore_tabs=parser_options['ignore_tabs'],
                                    single_line_comment=parser_options['single_line_comment'],
                                    java_style_comments=parser_options['java_style_comments'])
        auto_column_types = []
        if lines:
            delim, fields_list = _readfields(lines, parser_options['delimiters'])
            if len(fields_list) < 2:
                raise Exception('Not enough data to preview')

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
            parser_options['file_processor_type'] = processor.TYPE
            parser_options = _text_preview_convert(lines, parser_options)
            return parser_options
    else:
        # Even TextFileReader doesn't work
        msg = 'No input data was found'
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


HIVE_STRING_IDX = 0
HIVE_TINYINT_IDX = 1
HIVE_SMALLINT_IDX = 2
HIVE_INT_IDX = 3
HIVE_BIGINT_IDX = 4
HIVE_BOOLEAN_IDX = 5
HIVE_FLOAT_IDX = 6
HIVE_DOUBLE_IDX = 7
HIVE_TIMESTAMP_IDX = 8
HIVE_DECIMAL_IDX = 9
HIVE_BINARY_IDX = 10
HIVE_PRIMITIVES_LEN = len(hcatalog.forms.HIVE_PRIMITIVE_TYPES)


class HiveTypeAutoDefine(object):

    def isStrFloatingPointValue(self, strVal):
        return re.match(r'(^[+-]?((?:\d+\.\d+)|(?:\.\d+))(?:[eE][+-]?\d+)?$)', strVal) is not None

    def isStrIntegerValue(self, strVal):
        return re.match(r'(^[+-]?\d+(?:[eE][+]?\d+)?$)', strVal) is not None

    def isStrBooleanValue(self, strVal):
        return strVal == 'TRUE' or strVal == 'FALSE'

    def isIntHiveTinyint(self, intVal):
        return -2 ** 7 <= intVal <= 2 ** 7 - 1

    def isIntHiveSmallint(self, intVal):
        return -2 ** 15 <= intVal <= 2 ** 15 - 1

    def isIntHiveInt(self, intVal):
        return -2 ** 31 <= intVal <= 2 ** 31 - 1

    def isIntHiveBigint(self, intVal):
        return -2 ** 63 <= intVal <= 2 ** 63 - 1

    def isStrJdbcCompliantTimestamp(self, strVal):  # YYYY-MM-DD HH:MM:SS.fffffffff
        return re.match(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}(?:.\d{9})?$', strVal) is not None

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
        elif self.isStrJdbcCompliantTimestamp(strVal):
            return HIVE_TIMESTAMP_IDX
        return HIVE_STRING_IDX

    def defineFieldType(self, strVal):
        return hcatalog.forms.HIVE_PRIMITIVE_TYPES[self.defineFieldTypeIdx(strVal)]

    def defineColumnTypes(self, matrix, min_int_type=HIVE_BIGINT_IDX):
        column_types = []
        for row in matrix:
            if len(row) > len(column_types):
                for tmp in range(len(row) - len(column_types)):
                    column_types.append([0] * HIVE_PRIMITIVES_LEN)
            for i, field in enumerate(row):
                if field:
                    column_types[i][self.defineFieldTypeIdx(unicode(field), min_int_type=min_int_type)] += 1
        res_column_types = []
        for types_list in column_types:
            if types_list[HIVE_STRING_IDX] > 0:
                res_column_types.append(hcatalog.forms.HIVE_PRIMITIVE_TYPES[HIVE_STRING_IDX])
            elif types_list[HIVE_DOUBLE_IDX] > 0:
                res_column_types.append(hcatalog.forms.HIVE_PRIMITIVE_TYPES[HIVE_DOUBLE_IDX])
            elif types_list[HIVE_FLOAT_IDX] > 0:
                res_column_types.append(hcatalog.forms.HIVE_PRIMITIVE_TYPES[HIVE_FLOAT_IDX])
            else:
                res_column_types.append(hcatalog.forms.HIVE_PRIMITIVE_TYPES[types_list.index(max(types_list))])
        return res_column_types
