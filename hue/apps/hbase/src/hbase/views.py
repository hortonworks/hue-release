#!/usr/bin/env python
# Licensed to Hortonworks, inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from desktop.lib.django_util import render
from api import get_client
import simplejson as json
from desktop.lib.exceptions_renderable import PopupException
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.http import require_http_methods


def index(request):
  return render('index.mako', request, {})


def table_list_json(request):
  client = get_client()
  tables = client.table_list()
  result = dict((table, client.is_table_enabled(table)) for table in tables)
  return HttpResponse(json.dumps(result))


def create_table(request):
  if request.method == "GET":
    return render('create_table.mako', request, {})
  else:
    try:
      cfs = json.loads(request.POST.get("data"))
      get_client().create_table(request.POST["table_name"], cfs)
      return redirect('/hbase')
    except Exception as ex:
      raise PopupException(ex)


def view_table(request, table):
  try:
    client = get_client() 
    is_enabled = client.is_table_enabled(table)
    table = client.get_table(table, False)     
    return render('view_table.mako', request, {"table": table, "is_enabled": is_enabled})
  except Exception as ex:
    raise PopupException(ex)


def browse_data(request, table):
  try:
    client = get_client()
    if not client.is_table_enabled(table):
        raise PopupException("Table is disabled.")
    table = client.get_table(table, False)
    return render('browse_data.mako', request, {"table": table})
  except Exception as ex:
    raise PopupException(ex)


def get_data_json(request, table):
  result = {}
  table = get_client().get_table(table, False)
  result["cfs"] = [k for k in table.families().iterkeys()]
  if request.REQUEST.get("query"):
    data = iter(table.rows(request.REQUEST.get("query").split(",")))
  else:
    data = table.scan(row_start=request.REQUEST.get("row_start"), row_stop=request.REQUEST.get("row_stop"))
  rows = []
  for i in xrange(21):
    try:
      r = data.next()
      row = [r[0]]
      cols = {}
      for k, v in r[1].iteritems():
        cf, column = k.split(":")
        cols.setdefault(cf, [])
        cols[cf].append({column: v})
      row.append(cols)
      rows.append(row)
    except StopIteration:
      break
  result["data"] = rows
  return HttpResponse(json.dumps(result))


def get_versions_json(request, table):
  row = request.REQUEST["row"]
  column = request.REQUEST["col"]
  table = get_client().get_table(table, False)
  cells = table.cells(row, column, include_timestamp=True)
  return HttpResponse(json.dumps(cells))


@require_http_methods(["DELETE", "POST"])
def delete_data(request, table):
  row = request.REQUEST["row"]
  column = request.REQUEST.get("col")
  try:
    if column and not isinstance(column, list):
      column = [column]
    table = get_client().get_table(table, False)
    table.delete(row, column)
    return HttpResponse(json.dumps({"status": "done"}))
  except Exception as ex:
    return HttpResponseServerError(str(ex))


@require_http_methods(["PUT", "POST"])
def edit_data(request, table):
  row = request.REQUEST["row"]
  column = request.REQUEST["col"]
  try:
    table = get_client().get_table(table, False)
    table.put(row, {column: request.REQUEST["val"]})
    return HttpResponse(json.dumps({"status": "done"}))
  except Exception as ex:
    return HttpResponseServerError(str(ex))


@require_http_methods(["POST"])
def disable_table(request, table):
  try:
    get_client().disable_table(table)
    return HttpResponse(json.dumps({"status": "done"}))
  except Exception as ex:
    return HttpResponseServerError(str(ex))


@require_http_methods(["POST"])
def enable_table(request, table):
  try:
    get_client().enable_table(table)
    return HttpResponse(json.dumps({"status": "done"}))
  except Exception as ex:
    return HttpResponseServerError(str(ex))


@require_http_methods(["DELETE", "POST"])
def drop_table(request, table):
  try:
    get_client().delete_table(table, True)
    return HttpResponse(json.dumps({"status": "done"}))
  except Exception as ex:
    return HttpResponseServerError(str(ex))


@require_http_methods(["POST"])
def compact_table(request, table):
  try:
    get_client().compact_table(table, bool(request.POST.get("compactionType", False)))
    return HttpResponse(json.dumps({"status": "done"}))
  except Exception as ex:
    return HttpResponseServerError(str(ex))


@require_http_methods(["PUT", "POST"])
def add_row(request, table):
  try:
    table = get_client().get_table(table, False)
    data = json.loads(request.POST["data"])
    table.put(data["row"], {data["column"]: data["value"]})
    return HttpResponse(json.dumps({"status": "done"}))
  except Exception as ex:
    return HttpResponseServerError(str(ex))
