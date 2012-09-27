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

from desktop.lib.django_util import render
import datetime
from hcatalog import db_utils

import logging
import re

from django import forms
from django.core import urlresolvers
from django.db.models import Q
from django.http import HttpResponse, QueryDict
from django.shortcuts import redirect
from django.utils.encoding import force_unicode
from django.utils import simplejson

from desktop.lib import django_mako
from desktop.lib.paginator import Paginator
from desktop.lib.django_util import copy_query_dict, format_preserving_redirect, render
from desktop.lib.django_util import login_notrequired, get_desktop_uri_prefix
from desktop.lib.django_util import render_injected, PopupException

from hadoop.fs.exceptions import WebHdfsException

from beeswaxd import BeeswaxService
from beeswaxd.ttypes import QueryHandle, BeeswaxException, QueryNotFoundException

import hcatalog.forms
from hcatalog import common
from hcatalog import db_utils
from hcatalog import models

from jobsub.parameterization import find_variables, substitute_variables

from filebrowser.views import location_to_url


LOG = logging.getLogger(__name__)

def index(request):
  return render('index.mako', request, dict(date=datetime.datetime.now()))
  
def show_tables(request):
  tables = db_utils.meta_client().get_tables("default", ".*")
  return render("show_tables.mako", request, dict(tables=tables, tbl_name=""))


def describe_table(request, table):
  table_obj = ""
  #table_obj = db_utils.meta_client().get_table("default", table)
  sample_results = None
  is_view = table_obj.tableType == 'VIRTUAL_VIEW'

  # Don't show samples if it's a view (HUE-526).
  if not is_view:
    # Show the first few rows
    hql = "SELECT * FROM `%s` %s" % (table, _get_browse_limit_clause(table_obj))
    query_msg = make_hcatalog_query(request, hql)
    try:
      sample_results = []#db_utils.execute_and_wait(request.user, query_msg, timeout_sec=5.0)
    except:
      # Gracefully degrade if we're unable to load the results.
      logging.exception("Failed to read table '%s'" % table)
      sample_results = None

  hdfs_link = location_to_url(request, table_obj.sd.location)
  load_form = hcatalog.forms.LoadDataForm(table_obj)
  return render("describe_table.mako", request, dict(
      table=table_obj,
      table_name=table,
      top_rows=sample_results and list(parse_results(sample_results.data)) or None,
      hdfs_link=hdfs_link,
      load_form=load_form,
      is_view=is_view
  ))

def drop_table(request, table):
  table_obj = db_utils.meta_client().get_table("default", table)
  is_view = table_obj.tableType == 'VIRTUAL_VIEW'

  if request.method == 'GET':
    # It may be possible to determine whether the table is
    # external by looking at db_utils.meta_client().get_table("default", table).tableType,
    # but this was introduced in Hive 0.5, and therefore may not be available
    # with older metastores.
    if is_view:
      title = "Do you really want to drop the view '%s'?" % (table,)
    else:
      title = "This may delete the underlying data as well as the metadata.  Drop table '%s'?" % table
    return render('confirm.html', request, dict(url=request.path, title=title))
  elif request.method == 'POST':
    if is_view:
      hql = "DROP VIEW `%s`" % (table,)
    else:
      hql = "DROP TABLE `%s`" % (table,)
    query_msg = make_hcatalog_query(request, hql)
    try:
      return execute_directly(request,
                               query_msg,
                               on_success_url=urlresolvers.reverse(show_tables))
    except BeeswaxException, ex:
      # Note that this state is difficult to get to.
#      error_message, log = expand_exception(ex)
      error = "Failed to remove %s.  Error: %s" % (table, "error_message")
      raise PopupException(error, title="Beeswax Error", detail=log)


def read_table(request, table):
  """View function for select * from table"""
  table_obj = db_utils.meta_client().get_table("default", table)
  hql = "SELECT * FROM `%s` %s" % (table, _get_browse_limit_clause(table_obj))
  query_msg = make_hcatalog_query(request, hql)
  try:
    return execute_directly(request, query_msg, tablename=table)
  except BeeswaxException, e:
    # Note that this state is difficult to get to.
#    error_message, log = expand_exception(e)
    error = "Failed to read table.  Error: " + "error_message"
    raise PopupException(error, title="HCatalog Error", detail=log)


def confirm_query(request, query, on_success_url=None):

#  mform = hcatalog.forms.query_form()
#  mform.bind()
#  mform.query.initial = dict(query=query)
  
  tables = db_utils.meta_client().get_tables("default", ".*")
  return render("show_tables.mako", request, dict(tables=tables, tbl_name=""))
#  return render('execute.mako', request, {
#    'form': mform,
#    'action': urlresolvers.reverse(execute_query),
#    'error_message': "None",
#    'design': None,
#    'on_success_url': on_success_url,
#  })

def _get_browse_limit_clause(table_obj):
  """Get the limit clause when browsing a partitioned table"""
  if table_obj.partitionKeys:
    limit = conf.BROWSE_PARTITIONED_TABLE_LIMIT.get()
    if limit > 0:
      return "LIMIT %d" % (limit,)
  return ""


_SEMICOLON_WHITESPACE = re.compile(";\s*$")
def _strip_trailing_semicolon(query):
  """As a convenience, we remove trailing semicolons from queries."""
  s = _SEMICOLON_WHITESPACE.split(query, 2)
  if len(s) > 1:
    assert len(s) == 2
    assert s[1] == ''
  return s[0]


def make_hcatalog_query(request, hql, query_form=None):
  """
  make_hcatalog_query(request, hql, query_type, query_form=None) -> BeeswaxService.Query object

  It sets the various configuration (file resources, fuctions, etc) as well.
  """
  query_msg = BeeswaxService.Query(query=hql, configuration=[])

  # Configure running user and group.
  query_msg.hadoop_user = request.user.username

  if query_form is not None:
    for f in query_form.settings.forms:
      query_msg.configuration.append(django_mako.render_to_string(
                                          "hql_set.mako", f.cleaned_data))
    for f in query_form.file_resources.forms:
      type = f.cleaned_data["type"]
      # Perhaps we should have fully-qualified URIs here already?
      path = request.fs.fs_defaultfs + f.cleaned_data["path"]
      query_msg.configuration.append(
        django_mako.render_to_string("hql_resource.mako", dict(type=type, path=path)))
    for f in query_form.functions.forms:
      query_msg.configuration.append(
        django_mako.render_to_string("hql_function.mako", f.cleaned_data))
  return query_msg


def execute_directly(request, query_msg, design=None, tablename=None,
                     on_success_url=None, on_success_params=None, **kwargs):

  return None

def parse_results(data):
  """
  Results come back tab-delimited, and this splits
  them back up into reasonable things.
  """
  def parse_result_row(row):
    return row.split("\t")
  for row in data:
    yield parse_result_row(row)


def load_table(request, table):
  """
  Loads data into a table.
  """
  table_obj = db_utils.meta_client().get_table("default", table)
  if request.method == "POST":
    form = hcatalog.forms.LoadDataForm(table_obj, request.POST)
    if form.is_valid():
      # TODO(philip/todd): When PathField might refer to non-HDFS,
      # we need a pathfield.is_local function.
      hql = "LOAD DATA INPATH"
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

      on_success_url = urlresolvers.reverse(describe_table, kwargs={'table': table})
      return confirm_query(request, hql, on_success_url)
  else:
    form = hcatalog.forms.LoadDataForm(table_obj)
    return render("load_table.mako", request, dict(form=form, table=table, action=request.get_full_path()))

def describe_partitions(request, table):
  table_obj = db_utils.meta_client().get_table("default", table)
  if len(table_obj.partitionKeys) == 0:
    raise PopupException("Table '%s' is not partitioned." % table)
  partitions = db_utils.meta_client().get_partitions("default", table, max_parts= -1)
  return render("describe_partitions.mako", request,
                dict(table=table_obj, partitions=partitions, request=request))

