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
from django.http import HttpResponse, QueryDict
from django.shortcuts import redirect
from django.utils.encoding import force_unicode
from django.utils import simplejson

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

def index(request):
  return render('index.mako', request, dict(date=datetime.datetime.now()))
  
def show_tables(request):
  tables, isError, error = hcat_client().get_tables()
  return render("show_tables.mako", request, dict(tables=tables, debug_info=''))
  

def describe_table(request, table):
  try:
      table_desc_extended = hcat_client().describe_table_extended(table)
      partitions = [{"values":[{"columnName":"p1","columnValue":"a"},{"columnName":"p2","columnValue":"a"}],"name":"p1='a',p2='a'"},{"values":[{"columnName":"p1","columnValue":"aaa"},{"columnName":"p2","columnValue":"bbb"}],"name":"p1='aaa',p2='bbb'"}]
      table_obj = {'tableName':table, 'columns':table_desc_extended['columns'], 'partitionKeys':table_desc_extended['partitionColumns'], 'partitions':partitions}
  except Exception:
    import traceback
    error = traceback.format_exc()
    raise PopupException('Error getting table description', title="Error getting table description", detail=error)
  load_form = hcatalog.forms.LoadDataForm(table_obj)
  return render("describe_table.mako", request, dict(
      table=table_obj,
      table_name=table,
      load_form=load_form,
  ))

def drop_table(request, table):

  if request.method == 'GET':
    title = "This may delete the underlying data as well as the metadata.  Drop table '%s'?" % table
    return render('confirm.html', request, dict(url=request.path, title=title))
  elif request.method == 'POST':  
    hcat_client().drop_table(table)
    tables, isError, error = hcat_client().get_tables()
    return render("show_tables.mako", request, dict(tables=tables, debug_info=''))


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
    out_hql = ''
    if form.is_valid():
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
