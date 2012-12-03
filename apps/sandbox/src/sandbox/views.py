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

from desktop.lib.django_util import render
from desktop.lib.exceptions import PopupException
from django.http import HttpResponse
from django.core import urlresolvers
from django.utils import simplejson as json

from subprocess import Popen, PIPE
import re
import datetime
import logging

LOG = logging.getLogger(__name__)

TUTORIAL_UPDATE_SCRIPT = 'bash /home/sandbox/tutorials/tutorials_app/run/run.sh'
COMPONENTS_VERSION_FILE = '/tmp/sandbox_component_versions.info'
TUTORIAL_VERSION_FILE = '/tmp/tutorials_version.info'

COMPONENT_LIST = ['sandbox', 'tutorials', 'pig', 'hive', 'hcatalog']

def index(request):
  if request.method == 'POST':
    on_success_url = urlresolvers.reverse(index)
    error = ''
    try:
      _updateTutorials()
    except Exception, ex:
      error = str(ex)
    result = {'on_success_url':on_success_url, 'components':_get_components(), 'error':error}
    return HttpResponse(json.dumps(result))
  return render('configuration.mako', request, {'components':_get_components()})

def _get_components():
  version_content_list = []
  try:
    file_obj = open(COMPONENTS_VERSION_FILE, 'r')
    version_content_list = file_obj.readlines()
    file_obj.close()
  except IOError, ex:
    msg = "Failed to open file '%s': %s" % (COMPONENTS_VERSION_FILE, ex)
    LOG.exception(msg)
    
  try:
    file_obj = open(TUTORIAL_VERSION_FILE, 'r')
    tutorial_version = file_obj.readlines()[0]
    file_obj.close()
  except IOError, ex:
    tutorial_version = "undefined"
    msg = "Failed to open file '%s': %s" % (TUTORIAL_VERSION_FILE, ex)
    LOG.exception(msg)

  components = [
        {'name':'Sandbox', 'version':_get_version('sandbox', version_content_list)},
        {'name':'Tutorials', 'version':tutorial_version, 'updateButton':True},
        {'name':'HCatalog', 'version':_get_version('hcatalog', version_content_list)}, 
        {'name':'Pig', 'version':_get_version('pig', version_content_list)},
        {'name':'Hive', 'version':_get_version('hive', version_content_list)},]
  return components

def _get_version(component, content_list):
  version = 'undefined'
  for version_content in content_list:
    if component in version_content:
      m = re.match(r"[\D\.-]*(?P<ver>\d[\d+\.-]+\d)[\D\.-]*", version_content)
      if m is not None:
        version = m.group('ver')
      break
  return version
  
def _updateTutorials():
  p = Popen(TUTORIAL_UPDATE_SCRIPT, shell=True, stdin=PIPE, stdout=None, stderr=PIPE, close_fds=True)
  answer, error = p.communicate()
  if error:
    msg = "Updating tutorials failed: %s" % (error)
    LOG.error(msg)
    if not 'FETCH_HEAD' in error:
      raise Exception(str(error))

