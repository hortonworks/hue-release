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


from django import forms
from django.core import urlresolvers
from django.db.models import Q
from django.http import HttpResponse, QueryDict, Http404
from django.shortcuts import redirect
from django.utils.encoding import force_unicode
from django.utils import simplejson as json
from django.utils.translation import ugettext as _

from desktop.lib import django_mako
from desktop.lib.paginator import Paginator
from desktop.lib.django_util import copy_query_dict, format_preserving_redirect, render
from desktop.lib.django_util import login_notrequired, get_desktop_uri_prefix
from desktop.lib.django_util import render_injected
from desktop.lib.exceptions import PopupException
from desktop.lib.django_util import render

from hadoop.fs.exceptions import WebHdfsException
from filebrowser.views import _do_newfile_save
from jobsub.parameterization import find_variables, substitute_variables
from filebrowser.views import location_to_url

import hcatalog.forms
from hcatalog import common
from hcatalog import models
from hcat_client import hcat_client
from templeton import Templeton
from beeswax.views import (authorized_get_design, safe_get_design, save_design,
                           _strip_trailing_semicolon, get_parameterization,
                           make_beeswax_query, explain_directly,
                           expand_exception, make_query_context, authorized_get_history,
                           _parse_query_context, _parse_out_hadoop_jobs, _get_browse_limit_clause,
                           _get_server_id_and_state, download, parse_results)
from beeswax.views import execute_directly as e_d, explain_directly as expl_d
from beeswax.forms import query_form, SaveResultsForm
from beeswax import db_utils
from beeswax.models import MetaInstall, SavedQuery, QueryHistory
from django.core import urlresolvers
from beeswax.design import HQLdesign
from beeswaxd.ttypes import BeeswaxException, QueryHandle

import time
from datetime import date, datetime
import logging
import os

LOG = logging.getLogger(__name__)


def show_tables(request):
    tables = []
    try:
      tables = hcat_client().get_tables()
    except Exception, ex:
      raise PopupException('Error on getting a table list', title="Error on getting a table list", detail=str(ex))
    return render("show_tables.mako", request, dict(tables=tables,))


def describe_table(request, table):
  try:
      table_desc_extended = hcat_client().describe_table_extended(table)
      is_table_partitioned = table_desc_extended['partitioned']
      partitions = []
      partitionColumns = []
      if is_table_partitioned:
          partitions = hcat_client().get_partitions(table)
          partitionColumns = table_desc_extended['partitionColumns']
      table_obj = {'tableName':table, 'columns':table_desc_extended['columns'], 'partitionKeys':partitionColumns, 'partitions':partitions}
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
  ))


def drop_table(request, table):
  if request.method == 'GET':
    title = "This may delete the underlying data as well as the metadata.  Drop table '%s'?" % table
    return render('confirm.html', request, dict(url=request.path, title=title))
  elif request.method == 'POST':
    tables = []
    try:
      hcat_client().drop_table(table)
      tables = hcat_client().get_tables()
    except Exception, ex:
      raise PopupException('Drop table', title="Drop table", detail=str(ex))
    return render("show_tables.mako", request, dict(tables=tables,))


def load_table(request, table):
  """
  Loads data into a table.
  """
  try:
    table_desc_extended = hcat_client().describe_table_extended(table)
    is_table_partitioned = table_desc_extended['partitioned']
    partitionColumns = []
    if is_table_partitioned:
      partitionColumns = table_desc_extended['partitionColumns']
    table_obj = {'tableName':table, 'columns':table_desc_extended['columns'], 'partitionKeys':partitionColumns}
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
      hql += "`%s`" % (table,)
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
      raise PopupException('Error loading data into the table', title="Error loading data into the table", detail=error)
    return read_table(request, table)
  else:
    form = hcatalog.forms.LoadDataForm(table_obj)
    return render("load_table.mako", request, dict(form=form, table=table, action=request.get_full_path()))


def do_load_table(request, create_hql):
    # start_job(request, out_hql)
    script_file = "/tmp/hive_%s.hcat" % datetime.now().strftime("%s")
    file = open(script_file, 'w+')
    file.write(create_hql)
    file.close()
    hcat_client().hive_cli(file=script_file)
    if os.path.exists(script_file):
        os.remove(script_file)


def start_job(request, script_query):
    t = Templeton(request.user.username)
    statusdir = "/tmp/.hcatjobs/%s" % datetime.now().strftime("%s")
    script_file = statusdir + "/script.hcat"
#    _do_newfile_save(request.fs, script_file, script_query, "utf-8")
#    job = t.hive_query(file=script_file, statusdir=statusdir)
    job = t.hive_query(execute=script_query, statusdir=statusdir)

#    return HttpResponse(json.dumps(
#        {"job_id": job['id'],
#         "text": "The Job has been started successfully.\
#You can check job status on the following <a href='%s'>link</a>" % reverse("single_job", args=[job['id']])}))


def browse_partition(request, table):
  if request.method == 'POST':
    try:
      partition_name = request.POST.get('partition_name')
      location = hcat_client().get_partition_location(table, partition_name)
      #location = hcat_client().describe_partition(table, partition_name)
      url = location_to_url(request, location)
      result = {'url':url}
      return HttpResponse(json.dumps(result))
    except Exception, ex:
      raise PopupException('Browse partition', title="Browse partition", detail=str(ex))


def drop_partition(request, table):
  if request.method == 'GET':
    title = "Do you really want to drop this partition?"
    return render('confirm.html', request, dict(url=request.path, title=title))
  elif request.method == 'POST':
    try:
      partition_name = request.POST.get('partition_name')
      hcat_client().drop_partition(table, partition_name)
    except Exception, ex:
      raise PopupException('Drop partition', title="Drop partition", detail=str(ex))
    return describe_table(request, table)


def pig_view(request, table=None):
    try:
        from pig.views import index as pig_view_for_hcat
    except:
        raise Http404
    pig_script = {}
    pig_script.update({'pig_script': 'A = LOAD \'{t}\';\nDUMP A;'.format(t=table), 'title': '{t}'.format(t=table), 'python_script': '' })
    return pig_view_for_hcat(request, pig_script=pig_script)


def hive_view(request, table=None):
    tables = db_utils.meta_client().get_tables("default", ".*")
    if not tables:
        examples_installed = MetaInstall.get().installed_example
        return render("index.mako", request, {'examples_installed': examples_installed})
    else:
        return execute_query(request, table=table)


def execute_query(request, design_id=None, table=None):
    authorized_get_design(request, design_id)
    error_message, log = None, None
    form = query_form()
    action = request.path
    design = safe_get_design(request, SavedQuery.HQL, design_id)
    on_success_url = request.REQUEST.get('on_success_url')
 
    for _ in range(1):
        if request.method == 'POST':
            form.bind(request.POST)
 
            to_explain = request.POST.has_key('button-explain')
            to_submit = request.POST.has_key('button-submit')
            # Always validate the saveform, which will tell us whether it needs explicit saving
            if not form.is_valid():
                break
            to_save = form.saveform.cleaned_data['save']
            to_saveas = form.saveform.cleaned_data['saveas']
            if to_saveas and not design.is_auto:
                # Save As only affects a previously saved query
                design = design.clone()
            if to_submit or to_save or to_saveas or to_explain:
                explicit_save = to_save or to_saveas
                design = save_design(request, form, SavedQuery.HQL, design, explicit_save)
                action = urlresolvers.reverse(execute_query, kwargs=dict(design_id=design.id))
 
            # We're not going to process the form. Simply re-render it.
            if not to_explain and not to_submit:
                break
 
            query_str = _strip_trailing_semicolon(form.query.cleaned_data["query"])
            query_server = db_utils.get_query_server(form.query_servers.cleaned_data["server"])
            # (Optional) Parameterization.
            parameterization = get_parameterization(request, query_str, form, design, to_explain)
            if parameterization:
                return parameterization
 
            query_msg = make_beeswax_query(request, query_str, form)
            try:
                if to_explain:
                    return expl_d(request, query_str, query_msg, design, query_server)
                else:
                    notify = form.query.cleaned_data.get('email_notify', False)
                    return e_d(request, query_msg, design=design,
                               on_success_url=on_success_url,
                               notify=notify)
            except BeeswaxException, ex:
                error_message, log = expand_exception(ex)
                # Fall through to re-render the execute form.
        else:
            # GET request
            if design.id is not None:
                data = HQLdesign.loads(design.data).get_query_dict()
                form.bind(data)
                form.saveform.set_data(design.name, design.desc)
            else:
                # New design
                form.bind()
 
 
    table='SELECT * FROM `{t}`'.format(t=table)
    return render('execute.mako', request, {
        'action': action, 'design': design, 'error_message': error_message,
        'form': form, 'log': log, 'on_success_url': on_success_url, 'table': table})


def read_table(request, table):
  """View function for select * from table"""
  table_obj = db_utils.meta_client().get_table("default", table)
  hql = "SELECT * FROM `%s` %s" % (table, _get_browse_limit_clause(table_obj))
  query_msg = make_beeswax_query(request, hql)
  try:
    return execute_directly(request, query_msg, tablename=table)
  except BeeswaxException, e:
    # Note that this state is difficult to get to.
    error_message, log = expand_exception(e)
    error = _("Failed to read table. Error: %(error)s") % {'error': error_message}
    raise PopupException(error, title=_("Beeswax Error"), detail=log)


def execute_directly(request, query_msg, design=None, tablename=None,
                     on_success_url=None, on_success_params=None, **kwargs):
  """
  execute_directly(request, query_msg, tablename, design) -> HTTP response for execution

  This method wraps around db_utils.execute_directly() to take care of the HTTP response
  after the execution.

    query_msg
      The thrift Query object.

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
  history_obj = db_utils.execute_directly(request.user, query_msg, design, **kwargs)
  watch_url = urlresolvers.reverse("hcatalog.views.watch_query", kwargs=dict(id=history_obj.id))

  # Prepare the GET params for the watch_url
  get_dict = QueryDict(None, mutable=True)
  # (1) context
  if design:
    get_dict['context'] = make_query_context("design", design.id)
  elif tablename:
    get_dict['context'] = make_query_context("table", tablename)

  # (2) on_success_url
  if on_success_url:
    if callable(on_success_url):
      on_success_url = on_success_url(history_obj)
    get_dict['on_success_url'] = on_success_url

  # (3) misc
  if on_success_params:
    get_dict.update(on_success_params)

  return format_preserving_redirect(request, watch_url, get_dict)
  
  
def watch_query(request, id):
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
  id = int(id)

  query_history = authorized_get_history(request, id, must_exist=True)

  # GET param: context.
  context_param = request.GET.get('context', '')

  # GET param: on_success_url. Default to view_results
  results_url = urlresolvers.reverse(view_results, kwargs=dict(id=str(id), first_row=0))
  on_success_url = request.GET.get('on_success_url')
  if not on_success_url:
    on_success_url = results_url

  # Get the server_id
  server_id, state = _get_server_id_and_state(query_history)
  query_history.save_state(state)

  # Query finished?
  if state == QueryHistory.STATE.expired:
    raise PopupException(_("The result of this query has expired."))
  elif state == QueryHistory.STATE.available:
    return format_preserving_redirect(request, on_success_url, request.GET)
  elif state == QueryHistory.STATE.failed:
    # When we fetch, Beeswax server will throw us a BeeswaxException, which has the
    # log we want to display.
    return format_preserving_redirect(request, results_url, request.GET)

  # Still running
  log = db_utils.db_client(query_history.get_query_server()).get_log(server_id)

  # Keep waiting
  # - Translate context into something more meaningful (type, data)
  context = _parse_query_context(context_param)
  return render('watch_wait.mako', request, {
                      'query': query_history,
                      'fwd_params': request.GET.urlencode(),
                      'log': log,
                      'hadoop_jobs': _parse_out_hadoop_jobs(log),
                      'query_context': context,
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
  # Coerce types; manage arguments
  id = int(id)
  first_row = long(first_row)
  start_over = (first_row == 0)

  query_history = authorized_get_history(request, id, must_exist=True)

  handle = QueryHandle(id=query_history.server_id, log_context=query_history.log_context)
  context = _parse_query_context(request.GET.get('context'))

  # Retrieve query results
  try:
    results = db_utils.db_client(query_history.get_query_server()).fetch(handle, start_over, -1)
    assert results.ready, _('Trying to display result that is not yet ready. Query id %(id)s') % {'id': id}
    # We display the "Download" button only when we know
    # that there are results:
    downloadable = (first_row > 0 or len(results.data) > 0)
    fetch_error = False
  except BeeswaxException, ex:
    fetch_error = True
    error_message, log = expand_exception(ex)

  # Handle errors
  if fetch_error:
    return render('watch_results.mako', request, {
      'query': query_history,
      'error': True,
      'error_message': error_message,
      'log': log,
      'hadoop_jobs': _parse_out_hadoop_jobs(log),
      'query_context': context,
      'can_save': False,
    })

  log = db_utils.db_client(query_history.get_query_server()).get_log(query_history.server_id)
  download_urls = {}
  if downloadable:
    for format in common.DL_FORMATS:
      download_urls[format] = urlresolvers.reverse(
                                    download, kwargs=dict(id=str(id), format=format))

  save_form = SaveResultsForm()

  # Display the results
  return render('watch_results.mako', request, {
    'error': False,
    'query': query_history,
    # Materialize, for easier testability.
    'results': list(parse_results(results.data)),
    'has_more': results.has_more,
    'next_row': results.start_row + len(results.data),
    'start_row': results.start_row,
    'expected_first_row': first_row,
    'columns': results.columns,
    'download_urls': download_urls,
    'log': log,
    'hadoop_jobs': _parse_out_hadoop_jobs(log),
    'query_context': context,
    'save_form': save_form,
    'can_save': query_history.owner == request.user,
  })