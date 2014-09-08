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
import sys
import time

from multiprocessing import Process
from desktop.lib.django_util import render
from desktop.lib.paths import get_run_root, get_var_root
from desktop.lib.exceptions_renderable import PopupException
from desktop import conf as desktop_conf
from django.http import HttpResponse
import simplejson as json

from sh import ErrorReturnCode
try:
  from sh import bash, sudo
except ImportError:
  pass

from about import conf
import subprocess

LOG = logging.getLogger(__name__)

HUE_VERSION = "2.6.1"  # default version if VERSIONS file not exists

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
  if conf.SANDBOX.get():
    version = conf.SANDBOX_VERSION.get()
  else:
    version = HUE_VERSION
  return render('index.mako', request, {
    'components': components,
    'about_top_html': desktop_conf.CUSTOM.ABOUT_TOP_HTML.get(),
    'page_title': conf.ABOUT_PAGE_TITLE.get().replace("<br>", " "),
    'hue_title': conf.ABOUT_TITLE.get(),
    'hue_version': version,
    'ambari_status': _get_ambari_status()
  })

# ====== Ambari =======

def ambari(request, action):
  if request.method == 'POST':
    action = action.lower()
    if action == 'enable':
      return _enable_ambari(request)
    elif action == 'disable':
      return _disable_ambari(request)
    elif action == 'status':
      return _ambari_status(request)

def _fork(kill_parent=False, do_in_fork=None):
    try:
        pid = os.fork()
        if pid == 0:
          if do_in_fork:
            do_in_fork()
        else:
          if kill_parent:
            sys.exit(0)
    except OSError, e: 
        print >>sys.stderr, 'Unable to fork: %d (%s)' % (e.errno, e.strerror)
        sys.exit(1)

def ambari_fork_start():
  def _in_fork():
    # remove references from the main process
    os.chdir('/')
    os.setsid()
    os.umask(0)

    def _doublefork():
      subprocess.call("sudo service ambari start", shell=True)

    _fork(kill_parent=True, do_in_fork=_doublefork)
    sys.exit(0)

  _fork(kill_parent=True, do_in_fork=_in_fork)

def _enable_ambari(request):
  error = ''
  ret = ''
  try:
    ret = sudo.chkconfig("ambari", "on").stdout

    # FIXME: sh module uses os.fork() to create child process, which is not appropriate to run ambari
    # ret += sudo.service("ambari", "start").stdout
    p = Process(target=ambari_fork_start)
    p.start()
    time.sleep(10)
    # subprocess.Popen(["sudo", "service", "ambari", "start"])
  except Exception, ex:
    error = unicode(ex)
  result = {
    'return': ret,
    'error': error
  }
  return HttpResponse(json.dumps(result))

def _disable_ambari(request):
  error = ''
  ret = ''
  try:
    ret = sudo.chkconfig("ambari", "off").stdout
    # ret += sudo.service("ambari", "stop").stdout
    subprocess.Popen(["sudo", "service", "ambari", "stop"])
  except Exception, ex:
    error = unicode(ex)
  result = {
    'return': ret,
    'error': error
  }
  return HttpResponse(json.dumps(result))

def _get_ambari_status():
  """Returns True if ambari-agent started and False otherwise."""
  try:
    from sh import ambari_server
    output = ambari_server("status")
    if "not running" in output.stdout:
      return False
  except (ErrorReturnCode, ImportError):
    return False
  return True

def _ambari_status(request):
  val = "on" if _get_ambari_status() else "off"
  result = {
    'return': val,
  }
  return HttpResponse(json.dumps(result))

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
  global HUE_VERSION
  components = []
  try:
    with open(filename) as f:
      for line in f:
        l = line.strip().split("=")
        if len(l) < 2 or line.strip()[:1] == '#':
          continue
        component, version = l
        if len(version.strip()) == 0:
          continue
        if component == "HUE_VERSION":
          HUE_VERSION, buildnumber = version.split("-")
          components.append(('Hue', version))
        elif component == "Sandbox":
          components.append(('Sandbox Build', version))
        elif component == "Ambari-server":
          components.append(('Ambari', version))
        else:
          components.append((component, version))
  except Exception, ex:
    msg = 'Exception occurred processing file "%s": %s' % (filename, ex)
    LOG.error(msg)
    raise PopupException(msg)
  return components

def _get_components():
  components = []
  try:
    components += _read_versions(os.path.join(get_run_root(), "VERSIONS"))
    extra_versions_path = os.path.join(get_var_root(), "EXTRA_VERSIONS")
    if os.path.exists(extra_versions_path):
      components += _read_versions(extra_versions_path)
  except ValueError:#Exception:
    components = [
      ('HDP', "2.0.6"),
      ('Hadoop', "1.2.0.1.3.0.0-107"),
      ('HCatalog', "0.11.0.1.3.0.0-107"),
      ('Pig', "0.11.1.1.3.0.0-107"),
      ('Hive', "0.11.0.1.3.0.0-107"),
      ('Oozie', "3.3.2.1.3.0.0-107")
    ]

  if conf.TUTORIALS_INSTALLED.get():
    components.insert(0, ('Tutorials', _get_tutorials_version()))
    # components.insert(0, ("Sandbox", conf.SANDBOX_VERSION.get()))
  return components, HUE_VERSION
