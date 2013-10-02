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
from desktop.lib.paths import get_run_root, get_var_root
from django.http import HttpResponse
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
      'tutorials': _get_tutorials_version(),
      'error': error
    }
    return HttpResponse(json.dumps(result))
  components, HUE_VERSION = _get_components()
  return render('index.mako', request, {
    'components': components,
    'hue_version': HUE_VERSION,
  })

def _get_tutorials_version():
  TUTORIAL_VERSION_FILE = os.path.join(conf.TUTORIALS_PATH.get(), 'version')
  try:
    with open(TUTORIAL_VERSION_FILE, 'r') as file_obj:
      tutorial_version = file_obj.readlines()[0].strip()
  except IOError, ex:
    tutorial_version = "undefined"
    msg = "Failed to open file '%s': %s" % (TUTORIAL_VERSION_FILE, ex)
    LOG.error(msg)
  return tutorial_version


def _read_versions(filename):
  components = []
  with open(filename) as f:
    for line in f:
      l = line.strip().split("=")
      if len(l) < 2 or line.strip()[:1] == '#':
        continue
      component, version = l
      if component == "HUE_VERSION":
        HUE_VERSION, buildnumber = version.split(":")
        components.append(('Hue', version))
      elif component == "Sandbox":
        components.append(('Sandbox Build', version))
      else:
        components.append((component, version))
  return components


def _get_components():
  components = []
  HUE_VERSION = "2.3.0"
  try:
    components += _read_versions(os.path.join(get_run_root(), "VERSIONS"))
    extra_versions_path = os.path.join(get_var_root(), "EXTRA_VERSIONS")
    if os.path.exists(extra_versions_path):
      components += _read_versions(extra_versions_path)
  except ValueError:#Exception:
    components = [
      ('HDP', "2.0.5"),
      ('Hadoop', "1.2.0.1.3.0.0-107"),
      ('HCatalog', "0.11.0.1.3.0.0-107"),
      ('Pig', "0.11.1.1.3.0.0-107"),
      ('Hive', "0.11.0.1.3.0.0-107"),
      ('Oozie', "3.3.2.1.3.0.0-107")
    ]

  if conf.TUTORIALS_INSTALLED.get():
    components.insert(0, ('Tutorials', _get_tutorials_version()))
    components.insert(0, ("Sandbox", conf.SANDBOX_VERSION.get()))
  return components, HUE_VERSION
