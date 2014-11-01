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
from django.http import HttpResponse, QueryDict, Http404
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from django.template.defaultfilters import escapejs

from desktop.lib import django_mako
from desktop.lib.django_util import (format_preserving_redirect, render)
from desktop.lib.exceptions_renderable import PopupException
from desktop.context_processors import get_app_name

from filebrowser.views import location_to_url

import hcatalog.forms
from hcatalog import common
from hcat_client import HCatClient
from beeswax import conf
from beeswax.views import (authorized_get_design, safe_get_design, save_design,
                           get_parameterization, _get_query_handle_and_state,
                           authorized_get_history, confirm_query,
                           _parse_query_context, _parse_out_hadoop_jobs,
                           _get_current_db, _get_db_choices, download as beeswax_download, _clean_session)
from beeswax.forms import QueryForm, SaveResultsForm
from beeswax.models import SavedQuery, QueryHistory, make_query_context
from beeswax.design import HQLdesign
from beeswax.server import dbms
from beeswax.server.dbms import expand_exception, get_query_server_config, NoSuchObjectException

import logging
import time

LOG = logging.getLogger(__name__)


def index(request):
    database = _get_current_db(request, _get_last_database(request))
    return show_tables(request, database=database)

def show_databases(request):
    if request.method == 'POST':
        resp = {}
        try:
            databases = HCatClient(request.user.username).get_databases(like="*")
            databases_list_rendered = django_mako.render_to_string("database_list.mako", dict(
                app_name=get_app_name(request),
                databases=databases))
        except Exception as ex:
            resp['error'] = escapejs(ex.message)
        else:
            resp['database_list_rendered'] = databases_list_rendered
            resp['databases'] = databases
        return HttpResponse(json.dumps(resp))
    return render("show_databases.mako", request, {})


def show_tables(request, database=None):
    if database is None:
        database = _get_last_database(request, database)
    if request.method == 'POST':
        resp = {}
        try:
            tables = _get_table_list(request, database)
            table_list_rendered = django_mako.render_to_string("table_list.mako", dict(
                app_name=get_app_name(request),
                database=database,
                tables=tables,
            ))
        except Exception as ex:
            resp['error'] = escapejs(ex.message)
        else:
            resp['table_list_rendered'] = table_list_rendered
            resp['tables'] = tables
        return HttpResponse(json.dumps(resp))

    db = dbms.get(request.user)
    databases = db.get_databases()
    db_form = hcatalog.forms.DbForm(initial={'database': database}, databases=databases)
    response = render("show_tables.mako", request, {
        'database': database,
        'db_form': db_form,
    })
    response.set_cookie("hueHcatalogLastDatabase", database, expires=90)
    return response


def create_database(request):
    error = None
    if request.method == "POST":
        try:
            data = request.POST.copy()
            data.setdefault("use_default_location", False)
            db = dbms.get(request.user)
            databases = db.get_databases()
            form = hcatalog.forms.CreateDatabaseForm(data)
            form.database_list = databases

            if form.is_valid():
                database = form.cleaned_data['db_name']
                comment = form.cleaned_data['comment']
                location = None
                if not form.cleaned_data['use_default_location']:
                    location = form.cleaned_data['external_location']
                hcat_cli = HCatClient(request.user.username)
                hcat_cli.create_database(database=database, comment=comment, location=location)
                return render("show_databases.mako", request, {})
        except Exception as ex:
            error = ex.message
    else:
        form = hcatalog.forms.CreateDatabaseForm()

    return render("create_database.mako", request, dict(
        database_form=form,
        error=error
    ))


def describe_table_json(request, database, table):
    try:
        db = dbms.get(request.user)
        table = db.get_table(database, table)
        result = {"columns": [{"type": col.type, "name": col.name} for col in table.cols]}
    except NoSuchObjectException, e:
        result = {"status": "failure", 'failureInfo' : unicode(table+' table not found')}
    except Exception, e:
        result = {"status": "failure", 'failureInfo': unicode(e)}
    return HttpResponse(json.dumps(result))


def describe_table(request, database, table):
    try:
        table_desc_extended = HCatClient(request.user.username).describe_table_extended(table, db=database)
        is_table_partitioned = table_desc_extended['partitioned']
        partitions = []
        partitionColumns = []
        if is_table_partitioned:
            partitions = HCatClient(request.user.username).get_partitions(table, db=database)
            partitionColumns = table_desc_extended['partitionColumns']
        table_obj = {'tableName': table, 'columns': table_desc_extended['columns'], 'partitionKeys': partitionColumns,
                     'partitions': partitions}
    except Exception:
        import traceback

        error = traceback.format_exc()
        raise PopupException('Error getting table description', title="Error getting table description", detail=error)
    load_form = hcatalog.forms.LoadDataForm(table_obj)
    return render("describe_table.mako", request, dict(
        table=table_obj,
        table_name=table,
        load_form=load_form,
        is_table_partitioned=is_table_partitioned,
        database=database,
    ))


def drop_database(request):
    if request.method == 'GET':
        title = _("Do you really want to delete the database(s)?")
        return render('confirm.html', request, dict(url=request.path, title=title))
    elif request.method == 'POST':
        resp = {}
        try:
            for database in request.POST.getlist('database_selection'):
                HCatClient(request.user.username).drop_database(database, if_exists=True, option="cascade")
        except Exception as ex:
            resp['error'] = escapejs(ex.message)
        else:
            on_success_url = urlresolvers.reverse(get_app_name(request) + ':show_databases')
            resp['on_success_url'] = on_success_url
        return HttpResponse(json.dumps(resp))


def drop_table(request, database=None):
    if request.method == 'GET':
        title = _("Do you really want to delete the table(s)?")
        return render('confirm.html', request, dict(url=request.path, title=title))
    elif request.method == 'POST':
        database = _get_last_database(request, database)
        resp = {}
        try:
            tables = request.POST.getlist('table_selection')
            for table in tables:
                HCatClient(request.user.username).drop_table(table, db=database)
        except Exception as ex:
            resp['error'] = escapejs(ex.message)
        else:
            on_success_url = urlresolvers.reverse(get_app_name(request) + ':index')
            resp['on_success_url'] = on_success_url
        return HttpResponse(json.dumps(resp))


def load_table(request, database, table):
    """
    Loads data into a table.
    """
    try:
        table_desc_extended = HCatClient(request.user.username).describe_table_extended(table, db=database)
        is_table_partitioned = table_desc_extended['partitioned']
        partitionColumns = []
        if is_table_partitioned:
            partitionColumns = table_desc_extended['partitionColumns']
        table_obj = {'tableName': table, 'columns': table_desc_extended['columns'], 'partitionKeys': partitionColumns}
    except Exception:
        import traceback

        error = traceback.format_exc()
        raise PopupException('Error getting table description', title="Error getting table description", detail=error)
    if request.method == "POST":
        form = hcatalog.forms.LoadDataForm(table_obj, request.POST)
        hql = ''
        if form.is_valid():
            hql += "LOAD DATA INPATH"
            hql += " '%s'" % form.cleaned_data['path']
            if form.cleaned_data['overwrite']:
                hql += " OVERWRITE"
            hql += " INTO TABLE "
            hql += "`%s.%s`" % (database, table)
            if len(form.partition_columns) > 0:
                hql += " PARTITION ("
                vals = []
                for key, column_name in form.partition_columns.iteritems():
                    vals.append("%s='%s'" % (column_name, form.cleaned_data[key]))
                hql += ", ".join(vals)
                hql += ")"
            hql += ";"
        try:
            do_load_table(request, hql)
        except Exception:
            import traceback

            error = traceback.format_exc()
            raise PopupException('Error loading data into the table', title="Error loading data into the table",
                                 detail=error)
        on_success_url = urlresolvers.reverse(get_app_name(request) + ':describe_table',
                                              kwargs=dict(database=database, table=table))
        result = {'on_success_url': on_success_url}
        return HttpResponse(json.dumps(result))
    else:
        form = hcatalog.forms.LoadDataForm(table_obj)
        return render("load_table.mako", request, dict(form=form, table=table, action=request.get_full_path()))


def do_load_table(request, create_hql):
    HCatClient(request.user.username).do_hive_query_and_wait(execute=create_hql)


def browse_partition(request, database, table):
    if request.method == 'POST':
        try:
            partition_name = request.POST.get('partition_name')
            location = HCatClient(request.user.username).get_partition_location(table, partition_name, db=database)
            url = location_to_url(request, location)
            result = {'url': url}
            return HttpResponse(json.dumps(result))
        except Exception as ex:
            raise PopupException('Browse partition', title="Browse partition", detail=str(ex))


def drop_partition(request, database, table):
    if request.method == 'GET':
        title = "Do you really want to drop this partition?"
        return render('confirm.html', request, dict(url=request.path, title=title))
    elif request.method == 'POST':
        try:
            partition_name = request.POST.get('partition_name')
            HCatClient(request.user.username).drop_partition(table, partition_name, db=database)
        except Exception as ex:
            raise PopupException('Drop partition', title="Drop partition", detail=str(ex))
        on_success_url = urlresolvers.reverse(get_app_name(request) + ':describe_table',
                                              kwargs=dict(database=database, table=table))
        result = {'on_success_url': on_success_url}
        return HttpResponse(json.dumps(result))


def pig_view(request, database=None, table=None):
    database = _get_last_database(request, database)
    try:
        from pig.views import index as pig_view_for_hcat
    except:
        raise Http404
    request.session['autosave'] = {
        "pig_script": 'A = LOAD \'%s.%s\' USING org.apache.hive.hcatalog.pig.HCatLoader();\nDUMP A;' % (
            database if database else "default", table),
        'title': '%s' % table,
        'arguments': "-useHCatalog"
    }
    return pig_view_for_hcat(request)


def hive_view(request, database=None, table=None):
    database = _get_last_database(request, database)
    query_msg = ''
    if table is not None:
        query_msg = 'SELECT * FROM `%s.%s`;' % (database if database else "default", table)
    return confirm_query(request, query_msg)


def execute_query(request, design_id=None):
  """
  View function for executing an arbitrary query.
  It understands the optional GET/POST params:

    on_success_url
      If given, it will be displayed when the query is successfully finished.
      Otherwise, it will display the view query results page by default.
  """
  authorized_get_design(request, design_id)

  request.session['start_time'] = time.time()  # FIXME: add job id to not intersect simultaneous jobs
  error_message = None
  form = QueryForm()
  action = request.path
  log = None
  app_name = get_app_name(request)
  query_type = SavedQuery.TYPES_MAPPING['beeswax']
  design = safe_get_design(request, query_type, design_id)
  on_success_url = request.REQUEST.get('on_success_url')

  query_server = get_query_server_config(app_name)
  db = dbms.get(request.user, query_server)
  databases = _get_db_choices(request)


  if request.method == 'POST':
    form.bind(request.POST)
    form.query.fields['database'].choices =  databases # Could not do it in the form

    to_explain = request.POST.has_key('button-explain')
    to_submit = request.POST.has_key('button-submit')

    # Always validate the saveform, which will tell us whether it needs explicit saving
    if form.is_valid():
      to_save = form.saveform.cleaned_data['save']
      to_saveas = form.saveform.cleaned_data['saveas']

      if to_save or to_saveas:
        if 'beeswax-autosave' in request.session:
          del request.session['beeswax-autosave']

      if to_saveas and not design.is_auto:
        # Save As only affects a previously saved query
        design = design.clone()

      if to_submit or to_save or to_saveas or to_explain:
        explicit_save = to_save or to_saveas
        design = save_design(request, form, query_type, design, explicit_save)
        action = urlresolvers.reverse(app_name + ':execute_query', kwargs=dict(design_id=design.id))

      if to_explain or to_submit:
        query_str = form.query.cleaned_data["query"]

        if conf.CHECK_PARTITION_CLAUSE_IN_QUERY.get():
          query_str = _strip_trailing_semicolon(query_str)
          # check query. if a select query on partitioned table without partition keys,
          # intercept it and raise a PopupException.
          _check_partition_clause_in_query(form.query.cleaned_data.get('database', None), query_str, db)

        # (Optional) Parameterization.
        parameterization = get_parameterization(request, query_str, form, design, to_explain)
        if parameterization:
          return parameterization

        try:
          query = HQLdesign(form, query_type=query_type)
          if to_explain:
            return explain_directly(request, query, design, query_server)
          else:
            download = request.POST.has_key('download')

            download_format = form.query.cleaned_data.get('download_format', None)
            if not download_format: download_format = None
            if download_format in common.DL_FORMATS:
              request.session['dl_status'] = True

            return execute_directly(request, query, query_server, design, on_success_url=on_success_url, download_format=download_format, download=download)
        except QueryServerException, ex:
          error_message, log = expand_exception(ex, db)
  else:
    if design.id is not None:
      data = HQLdesign.loads(design.data).get_query_dict()
      form.bind(data)
      form.saveform.set_data(design.name, design.desc)
    else:
      # New design
      form.bind()
      if 'beeswax-autosave' in request.session:
        form.query.fields['query'].initial = request.session['beeswax-autosave']['query']

    form.query.fields['database'].choices = databases # Could not do it in the form

  database = _get_current_db(request)
  response = render('execute.mako', request, {
    'action': action,
    'design': design,
    'error_message': error_message,
    'form': form,
    'log': log,
    'on_success_url': on_success_url,
    'show_execution_engine':conf.SHOW_EXECUTION_ENGINE.get(),
  })
  response.set_cookie("hueHcatalogLastDatabase", database, expires=90)
  return response


def hive_view_download(request, id, format):
  return beeswax_download(request, id, format)


def read_table(request, database, table):
    database = _get_last_database(request, database)
    db = dbms.get(request.user)
    table = db.get_table(database, table)
    try:
        partitions = db.get_partitions(database, table, max_parts=1) if table.partition_keys else None
        history = db.select_star_from(database, table, partitions)
        get = request.GET.copy()
        get['context'] = 'table:%s:%s' % (table.name, database)
        request.GET = get
        return watch_query(request, history.id)
    except Exception, e:
        raise PopupException(_('Could not read table'), detail=e)


def execute_directly(request, query, query_server=None, design=None, tablename=None,
                     on_success_url=None, on_success_params=None, download_format=None, **kwargs):
    """
    execute_directly(request, query_msg, tablename, design) -> HTTP response for execution

    This method wraps around dbms.execute_query() to take care of the HTTP response
    after the execution.

      query
        The HQL model Query object.

      query_server
        To which Query Server to submit the query.
        Dictionary with keys: ['server_name', 'server_host', 'server_port'].

      design
        The design associated with the query.

      tablename
        The associated table name for the context.

      on_success_url
        Where to go after the query is done. The URL handler may expect an option "context" GET
        param. (See ``watch_query``.) For advanced usage, on_success_url can be a function, in
        which case the on complete URL is the return of:
          on_success_url(history_obj) -> URL string
        Defaults to the view results page.

      on_success_params
        Optional params to pass to the on_success_url (in additional to "context").

    Note that this may throw a Beeswax exception.
    """
    if design is not None:
        authorized_get_design(request, design.id)

    db = dbms.get(request.user, query_server)
    database = query.query.get('database')
    if database is None:
        database = _get_last_database(request)
    db.use(database)

    history_obj = db.execute_query(query, design)

    watch_url = urlresolvers.reverse(get_app_name(request) + ':watch_query', kwargs={'id': history_obj.id, 'download_format':download_format})
    if 'download' in kwargs and kwargs['download']:
        watch_url += '?download=true'

    # Prepare the GET params for the watch_url
    get_dict = QueryDict(None, mutable=True)
    # (1) context
    if design:
        get_dict['context'] = make_query_context('design', design.id)
    elif tablename:
        get_dict['context'] = make_query_context('table', '%s:%s' % (tablename, database))

    # (2) on_success_url
    if on_success_url:
        if callable(on_success_url):
            on_success_url = on_success_url(history_obj)
        get_dict['on_success_url'] = on_success_url

    # (3) misc
    if on_success_params:
        get_dict.update(on_success_params)

    return format_preserving_redirect(request, watch_url, get_dict)


def explain_directly(request, query, design, query_server):
  explanation = dbms.get(request.user, query_server).explain(query)
  context = ("design", design)

  return render('explain.mako', request, dict(query=query, explanation=explanation.textual, query_context=context))


def watch_query(request, id, download_format=None):
    """
    Wait for the query to finish and (by default) displays the results of query id.
    It understands the optional GET params:

      on_success_url
        If given, it will be displayed when the query is successfully finished.
        Otherwise, it will display the view query results page by default.

      context
        A string of "name:data" that describes the context
        that generated this query result. It may be:
          - "table":"<table_name>"
          - "design":<design_id>

    All other GET params will be passed to on_success_url (if present).
    """
    # Coerce types; manage arguments
    query_history = authorized_get_history(request, id, must_exist=True)
    db = dbms.get(request.user, query_history.get_query_server_config())

    # GET param: context.
    context_param = request.GET.get('context', '')

    # GET param: on_success_url. Default to view_results
    if request.session.get('dl_status', False)==False and download_format in common.DL_FORMATS:
      results_url = urlresolvers.reverse(get_app_name(request) + ':execute_query')
    else:
      results_url = urlresolvers.reverse(get_app_name(request) + ':view_results', kwargs={'id': id, 'first_row': 0})
    if request.GET.get('download', ''):
        results_url += '?download=true'
    on_success_url = request.GET.get('on_success_url')
    if not on_success_url:
        on_success_url = results_url

    # Go to next statement if asked to continue or when a statement with no dataset finished.
    if request.method == 'POST' or (
            not query_history.is_finished() and query_history.is_success() and not query_history.has_results):
        try:
            query_history = db.execute_next_statement(query_history)
        except Exception:
            pass

    # Check query state
    handle, state = _get_query_handle_and_state(query_history)
    query_history.save_state(state)

    if query_history.is_failure():
        # When we fetch, Beeswax server will throw us a BeeswaxException, which has the
        # log we want to display.
        return format_preserving_redirect(request, results_url, request.GET)
    elif query_history.is_finished() or (query_history.is_success() and query_history.has_results):
        if request.session.get('dl_status', False):  # BUG-20020
          on_success_url = urlresolvers.reverse(get_app_name(request) + ':download', kwargs=dict(id=str(id), format=download_format))
        _clean_session(request)
        return format_preserving_redirect(request, on_success_url, request.GET)

    # Still running
    log = db.get_log(handle)

    # Keep waiting
    # - Translate context into something more meaningful (type, data)
    query_context = _parse_query_context(context_param)

    return render('watch_wait.mako', request, {
        'query': query_history,
        'fwd_params': request.GET.urlencode(),
        'log': log,
        'hadoop_jobs': _parse_out_hadoop_jobs(log)[0],
        'query_context': query_context,
        'download_format': download_format, ## ExpV
    })


def view_results(request, id, first_row=0):
    """
    Returns the view for the results of the QueryHistory with the given id.

    The query results MUST be ready.
    To display query results, one should always go through the watch_query view.

    If ``first_row`` is 0, restarts (if necessary) the query read.  Otherwise, just
    spits out a warning if first_row doesn't match the servers conception.
    Multiple readers will produce a confusing interaction here, and that's known.

    It understands the ``context`` GET parameter. (See watch_query().)
    """
    first_row = long(first_row)
    start_over = (first_row == 0)
    results = None
    data = None
    fetch_error = False
    error_message = ''
    log = ''
    app_name = get_app_name(request)

    query_history = authorized_get_history(request, id, must_exist=True)
    db = dbms.get(request.user, query_history.get_query_server_config())

    handle, state = _get_query_handle_and_state(query_history)
    context_param = request.GET.get('context', '')
    query_context = _parse_query_context(context_param)

    # To remove in Hue 2.3
    download = request.GET.get('download', '')

    # Update the status as expired should not be accessible
    expired = state == QueryHistory.STATE.expired
    if expired:
        state = QueryHistory.STATE.expired
        query_history.save_state(state)

    # Retrieve query results
    try:
        if not download:
            results = db.fetch(handle, start_over, 100)
            data = list(results.rows())  # Materialize results

            # We display the "Download" button only when we know that there are results:
            downloadable = first_row > 0 or data
        else:
            downloadable = True
            data = []
            results = type('Result', (object,), {
                'rows': 0,
                'columns': [],
                'has_more': False,
                'start_row': 0, })
        log = db.get_log(handle)
    except Exception as ex:
        fetch_error = True
        error_message, log = expand_exception(ex, db)

    # Handle errors
    error = fetch_error or results is None or expired

    context = {
        'error': error,
        'error_message': error_message,
        'has_more': True,
        'query': query_history,
        'results': data,
        'expected_first_row': first_row,
        'log': log,
        'hadoop_jobs': _parse_out_hadoop_jobs(log)[0],
        'query_context': query_context,
        'can_save': False,
        'context_param': context_param,
        'expired': expired,
        'app_name': app_name,
        'download': download,
    }

    if not error:
        download_urls = {}
        if downloadable:
            for format in common.DL_FORMATS:
                download_urls[format] = urlresolvers.reverse('beeswax' + ':download',
                                                             kwargs=dict(id=str(id), format=format))

        save_form = SaveResultsForm()
        results.start_row = first_row

        context.update({
            'results': data,
            'has_more': results.has_more,
            'next_row': results.start_row + len(data),
            'start_row': results.start_row,
            'expected_first_row': first_row,
            'columns': results.columns,
            'download_urls': download_urls,
            'save_form': save_form,
            'can_save': query_history.owner == request.user and not download,
        })

    return render('watch_results.mako', request, context)


def list_tables_json(request, database=None):
    """Returns a table list"""
    try:
        tables = _get_table_list(request, database)
    except Exception, e:
        tables = {"status": {"failureInfo": unicode(e)}}
    return HttpResponse(json.dumps(tables))


def list_databases_json(request):
    tree = {}
    # databases = HCatClient(request.user.username).get_databases(like="*")
    db = dbms.get(request.user)
    databases = db.get_databases()
    for database in databases:
        tables = _get_table_list(request, database)
        tree[database] = tables
    return HttpResponse(json.dumps(tree))


def _get_table_list(request, database=None):
    """Returns a table list"""
    database = _get_last_database(request, database)
    db = dbms.get(request.user)
    tables = db.get_tables(database=database)
    return tables


def _get_last_database(request, database=None):
    dbs = dbms.get(request.user).get_databases()
    if database is not None:
        LOG.debug("Getting database name from argument")
    elif request and request.method == 'POST' and request.POST.get('database'):
        database = request.POST.get('database')
        LOG.debug("Getting database name from request")
    elif request:
        database = request.COOKIES.get('hueHcatalogLastDatabase', 'default')
        if database in dbs:
            LOG.debug("Getting database name from cookies")
        else:
            database = 'default'
    return database


def listdir(request, path):
    return HttpResponse(json.dumps(request.fs.listdir(path)))


def ping_hive_job(request, job_id):
    try:
        result = HCatClient(request.user.username).check_job(job_id)
    except Exception as ex:
        result = {"status": {"failureInfo": unicode(ex)}}
    return HttpResponse(json.dumps(result))
