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

from django.conf import settings
from desktop.lib.django_util import render
from desktop.lib.exceptions import PopupException
from django.http import HttpResponse
from django.core import urlresolvers
from django.utils import simplejson as json

from subprocess import Popen, PIPE
import sandboxversions as versions

import re
import datetime
import logging

LOG = logging.getLogger(__name__)


TUTORIAL_UPDATE_SCRIPT = 'bash /home/sandbox/tutorials/tutorials_app/run/run.sh'
TUTORIAL_VERSION_FILE = '/tmp/tutorials_version.info'

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
  return render('index.mako', request, {'components':_get_components()})

def _get_components():
  try:
    file_obj = open(TUTORIAL_VERSION_FILE, 'r')
    tutorial_version = file_obj.readlines()[0]
    file_obj.close()
  except IOError, ex:
    tutorial_version = "undefined"
    msg = "Failed to open file '%s': %s" % (TUTORIAL_VERSION_FILE, ex)
    LOG.exception(msg)

  try: versions.SANDBOX_VERSION
  except:
    sandboxVer = 'undefined'
  else:
    sandboxVer = versions.SANDBOX_VERSION
  try: versions.HADOOP_VERSION
  except:
    hadoopVer = 'undefined'
  else:
    hadoopVer = versions.HADOOP_VERSION
  try: versions.HCATALOG_VERSION
  except:
    hcatalogVer = 'undefined'
  else:
    hcatalogVer = versions.HCATALOG_VERSION
  try: pigVer = versions.PIG_VERSION
  except:
    pigVer = 'undefined'
  else:
    pigVer = versions.PIG_VERSION
  try: versions.HIVE_VERSION
  except:
    hiveVer = 'undefined'
  else:
    hiveVer = versions.HIVE_VERSION

  components = [
        {'name':'Hadoop', 'version':hadoopVer},
        {'name':'Tutorials', 'version':tutorial_version, 'updateButton':True},
        {'name':'HCatalog', 'version':hcatalogVer},
        {'name':'Pig', 'version':pigVer},
        {'name':'Hive', 'version':hiveVer},]
  return components

def _updateTutorials():
  p = Popen(TUTORIAL_UPDATE_SCRIPT, shell=True, stdin=PIPE, stdout=None, stderr=PIPE, close_fds=True)
  answer, error = p.communicate()
  if error:
    msg = "Updating tutorials failed: %s" % (error)
    LOG.error(msg)
    if not 'FETCH_HEAD' in error:
      raise Exception(str(error))
