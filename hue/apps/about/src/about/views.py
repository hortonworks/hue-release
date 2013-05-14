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
import os
from desktop.lib.django_util import render
from django.http import HttpResponse
from django.core import urlresolvers
import simplejson as json

from sh import bash
from about import conf

LOG = logging.getLogger(__name__)


def index(request):
  if request.method == 'POST':
    error = ''
    try:
      bash(conf.TUTORIALS_UPDATE_SCRIPT.get())
    except Exception, ex:
      error = unicode(ex)
    result = {
      'components': _get_components(),
      'error': error
    }
    return HttpResponse(json.dumps(result))
  return render('index.mako', request, {
    'components': _get_components(),
    'hue_version': conf.HUE_VERSION.get(),
  })


def _get_components():
  components = {
    'Hadoop': conf.HADOOP_VERSION.get(),
    'HCatalog': conf.HCATALOG_VERSION.get(),
    'Pig': conf.PIG_VERSION.get(),
    'Hive': conf.HIVE_VERSION.get()
  }

  if conf.TUTORIALS_INSTALLED.get():
    TUTORIAL_VERSION_FILE = os.path.join(conf.TUTORIALS_PATH.get(), 'version')
    try:
      with open(TUTORIAL_VERSION_FILE, 'r') as file_obj:
        tutorial_version = file_obj.readlines()[0].strip()
    except IOError, ex:
      tutorial_version = "undefined"
      msg = "Failed to open file '%s': %s" % (TUTORIAL_VERSION_FILE, ex)
      LOG.error(msg)

    components['tutorials'] = tutorial_version
  return components
