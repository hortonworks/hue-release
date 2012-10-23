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

from desktop.lib import django_mako
from desktop.lib.paginator import Paginator
from desktop.lib.django_util import copy_query_dict, format_preserving_redirect, render
from desktop.lib.django_util import login_notrequired, get_desktop_uri_prefix
from desktop.lib.django_util import render_injected
from desktop.lib.exceptions import PopupException
from desktop.lib.django_util import render

from hadoop.fs.exceptions import WebHdfsException
from filebrowser.views import _do_newfile_save

from beeswax.views import read_table as beeswax_read_table

import hcatalog.forms
from hcatalog import common
from hcatalog import models
from hcat_client import hcat_client
from templeton import Templeton

from jobsub.parameterization import find_variables, substitute_variables
from filebrowser.views import location_to_url

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


def read_table(request, table):
  return beeswax_read_table(request, table)

 
def load_table(request, table):
  """
  Loads data into a table.
  """
  try:
    table_desc_extended = hcat_client().describe_table_extended(table)
    table_obj = {'tableName':table, 'columns':table_desc_extended['columns'], 'partitionKeys':table_desc_extended['partitionColumns']}
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
    return beeswax_read_table(request, table)
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
    table = 'A = LOAD \'{t}\';\nDUMP A;'.format(t=table)
    return pig_view_for_hcat(request, table=table)


from beeswax.views import (authorized_get_design, safe_get_design, save_design,
                           _strip_trailing_semicolon, get_parameterization,
                           make_beeswax_query, explain_directly, execute_directly,
                           expand_exception)
from beeswax.forms import query_form
from beeswax import db_utils
from beeswax.models import MetaInstall, SavedQuery
from django.core import urlresolvers
from beeswax.design import HQLdesign
from beeswaxd.ttypes import BeeswaxException


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
            # (Optional) Parameterization.
            parameterization = get_parameterization(request, query_str, form, design, to_explain)
            if parameterization:
                return parameterization

            query_msg = make_beeswax_query(request, query_str, form)
            try:
                if to_explain:
                    return explain_directly(request, query_str, query_msg, design)
                else:
                    notify = form.query.cleaned_data.get('email_notify', False)
                    return execute_directly(request, query_msg, design=design,
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

