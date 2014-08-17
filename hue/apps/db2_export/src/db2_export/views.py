#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
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
"""
Beeswax is a UI for Hive.
"""

import logging

from django.core import urlresolvers
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.django_util import render
from django.utils import simplejson
from django.http import HttpResponse

from beeswax import query_result, conf
from beeswax.query_result import QueryResult

from db2_export.models import ExportState
from db2_export import helper
from db2_export.controller import handle_export_request
import re
from cStringIO import StringIO
from db2_export.number import human_size, intcomma

LOG = logging.getLogger(__name__)

def export_state(request, id):
  try:
    state_id = int(id)
    state = ExportState.objects.get(id=state_id)
    if state.query_history.owner != request.user:
      data = dict(error="only available to the owner!")
    else: 
      if state.is_done():
        data = _extract_load_output(state_id)
      else:
        data = {}

      data["state"] = state.name
      data["size"] = human_size(state.size)
      data["finished_size"] = human_size(state.finished_size)
      data["finished_rows"] = intcomma(state.finished_rows)
  except ExportState.DoesNotExist:
    data = dict(error=("Invalid state id: %s" % id))
  return HttpResponse(simplejson.dumps(data),
        mimetype="application/json")

def export_table(request, table, dbname="default"):
  """
  export a Hive table to RDMS
  """
  raise PopupException(("Coming soon...\nExport %s.%s to DB2." % (dbname, table)))

import codecs
def export_data(request, id):
  result = query_result.create_from_request(request, int(id))
  file = codecs.open("/tmp/" + id + ".txt", "w", encoding="utf-8")
  size = 0
  nrows = 0
  for row in result.data_generator():
    file.write(row)
    file.write("\n")
    size  += len(row) + 1
    nrows += 1
  file.close()

  return HttpResponse("%d, %d" % (size, nrows), mimetype="text/html")

def export_results(request, id):
  id = int(id)
  result = query_result.create_from_request(request, id)
  try:
    _validate_query_result(result, request)
    template, params = handle_export_request(helper, request, result)
  except Exception, e:
    raise PopupException(str(e))
  return render(template, request, params)

PATTERN = re.compile(r"^Number of rows (\w+)\s*=\s*(\d+)$")

def export_output(request, state_id):
  state_id = int(state_id)
  state = ExportState.objects.get(id=state_id)
  if state.query_history.owner != request.user:
    msg = dict(error="only available to the owner!")
  elif state.is_done():
    msg = _extract_load_output()
  else:
    msg = dict(error="exporting is not done yet!")
  return HttpResponse(simplejson.dumps(msg),
        mimetype="application/json")

def _extract_load_output(state_id):
  msg = {}
  stdout = StringIO()
  try:
    path = "/tmp/bw-export-%d.out" % state_id
    file = open(path, "r")
    for line in file:
      stdout.write(line)
      m = PATTERN.match(line)
      if m:
        msg[m.group(1)] = intcomma(int(m.group(2)))
    msg["stdout"]=stdout.getvalue()
  except IOError as (errno, stderror):
    msg = dict(error="%d: %s" % (errno, stderror))
  finally:
    file.close()
  return msg

def _validate_query_result(result, request):
  msg = None
  if not result.owned_by(request.user):
    msg = 'This action is only available to the user who submitted the query.'
  elif result.is_expired():
    msg = 'This query results expired.'
  elif result.is_failed():
    msg = 'The query failed.'
  elif not result.is_ready():
    msg = 'The result of this query is not available yet.'
  else:
    limit = long(conf.EXPORT_LIMIT.get())
    if result.size() > limit:
      msg = 'The query result size (%s) exceeds the export limit %s' % (result.size(), limit)
  if msg: 
    raise PopupException(msg) 
    
