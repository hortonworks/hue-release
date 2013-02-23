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

import logging
from desktop.lib.django_util import render
from django.http import HttpResponse
from django.core import urlresolvers
import simplejson as json

from sh import bash
import sandboxversions as versions

LOG = logging.getLogger("analitics")

TUTORIAL_UPDATE_SCRIPT = '/home/sandbox/tutorials/tutorials_app/run/run.sh'
TUTORIAL_VERSION_FILE = '/home/sandbox/sandbox-tutorials/version'

def index(request):
  if request.method == 'POST':
    on_success_url = urlresolvers.reverse(index)
    error = ''
    try:
      bash(TUTORIAL_UPDATE_SCRIPT)
    except Exception, ex:
      error = str(ex)
    result = {'on_success_url':on_success_url, 'components':_get_components(), 'error':error}
    return HttpResponse(json.dumps(result))
  return render('index.mako', request, {'components':_get_components()})


def _get_components():
  try:
    with open(TUTORIAL_VERSION_FILE, 'r') as file_obj:
      tutorial_version = file_obj.readlines()[0]
  except IOError, ex:
    tutorial_version = "undefined"
    msg = "Failed to open file '%s': %s" % (TUTORIAL_VERSION_FILE, ex)
    LOG.exception(msg)

  components = [
        {'name':'Hadoop', 'version': versions.HADOOP_VERSION},
        {'name':'Tutorials', 'version':tutorial_version, 'updateButton':True},
        {'name':'HCatalog', 'version': versions.HCATALOG_VERSION},
        {'name':'Pig', 'version': versions.PIG_VERSION},
        {'name':'Hive', 'version': versions.HIVE_VERSION},]
  return components
