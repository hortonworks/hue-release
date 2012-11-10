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

import re
import datetime
import logging

LOG = logging.getLogger(__name__)

COMPONENT_LIST = ['sandbox', 'tutorials', 'pig', 'hive', 'hcatalog']

def index(request):
  version_content_list = []
  try:
    path = '/tmp/sandbox_component_versions.info'
    file_obj = open(path, 'r')
    version_content_list = file_obj.readlines()
    file_obj.close()
  except IOError, ex:
    msg = "Failed to open file '%s': %s" % (path, ex)
    LOG.exception(msg)
  components = [
        {'name':'Sandbox', 'version':_get_version('sandbox', version_content_list)},
        {'name':'Tutorials', 'version':_get_version('tutorials', version_content_list), 'updateButton':True},
        {'name':'HCatalog', 'version':_get_version('pig', version_content_list)}, 
        {'name':'Pig', 'version':_get_version('pig', version_content_list)},
        {'name':'Hive', 'version':_get_version('hive', version_content_list)},]
  return render('configuration.mako', request, {'components':components})

def _get_version(component, content_list):
  version = 'undefined'
  for version_content in content_list:
    if component in version_content:
      m = re.match(r"[\D\.-]*(?P<ver>[\d+\.-]+)[\.\D]*", version_content)
#      raise PopupException(str(''))
      if m is not None:
        version = m.group('ver')
      break
  return version