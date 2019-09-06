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
from __future__ import absolute_import

import calendar
import errno
import re
import logging
import tempfile
import posixpath
import time

from nose.tools import assert_not_equal
from hadoop.fs import normpath as fs_normpath
from azure.conf import get_default_abfs_fs

LOG = logging.getLogger(__name__)

ABFS_PATH_RE = re.compile('^/*[aA][bB][fF][sS]{1,2}://([$a-z0-9](?!.*--)[-a-z0-9]{1,61}[a-z0-9])(/(.*?)/?)?$')
ABFS_PATH_FULL = re.compile('^/*[aA][bB][fF][sS]{1,2}://(([$a-z0-9](?!.*--)[-a-z0-9]{1,61}[a-z0-9])@[^.]*?\.dfs\.core\.windows\.net)(/(.*?)/?)?$')#bug here
ABFS_ROOT_S = 'abfss://'
ABFS_ROOT = 'abfs://'
ABFSACCOUNT_NAME = re.compile('^/*[aA][bB][fF][sS]{1,2}://[$a-z0-9](?!.*--)[-a-z0-9]{1,61}[a-z0-9](@.*?)$')

def parse_uri(uri):
  """
  Returns filesystem_name, direct_name, base_direct_name
  Raises ValueError if invalid ABFS URI is passed.
  """
  match = ABFS_PATH_RE.match(uri)
  direct_name = ''
  base_direct_name = ''
  file_system = ''
  if match:
    direct_name = match.group(3) or ''
    base_direct_name = match.group(2) or ''
    file_system = match.group(1)
  else:
    match = ABFS_PATH_FULL.match(uri)
    if not match:
      raise ValueError("Invalid ABFS URI: %s" % uri)
    direct_name = match.group(4) or ''
    base_direct_name = match.group(3) or ''
    file_system = match.group(2)
  return file_system, direct_name, base_direct_name

def is_root(uri):
  """
  Checks if Uri is the Root Directory
  """
  return uri.lower() == ABFS_ROOT or uri.lower() == ABFS_ROOT_S


def strip_scheme(path):
  """
  returns the path without abfss:// or abfs://
  """
  try:
    filesystem, file_path = parse_uri(path)[:2]
  except:
    return path
  assert_not_equal(filesystem, '', 'File System must be Specified')
  path = filesystem + '/' + file_path
  return path
  
def strip_path(path):
  """
  Return only the end of a path given another path
  """
  if is_root(path):
    return path
  split_path = path.split('/')
  return split_path[len(split_path) - 1]

def normpath(path):
  """
  Return the normlized path, but ignore leading prefix if it exists
  """
  if is_root(path):
    return path
  elif path.lower().startswith(ABFS_ROOT):
    normalized = '%s%s' % (ABFS_ROOT, fs_normpath(path[len(ABFS_ROOT):]))
  elif path.lower().startswith(ABFS_ROOT_S):
    normalized = '%s%s' % (ABFS_ROOT_S, fs_normpath(path[len(ABFS_ROOT_S):]))
  else:
    normalized = fs_normpath(path)
  return normalized

def parent_path(path):
  """
  Returns the parent of the specified folder
  """
  if is_root(path):
    return path
  filesystem, directory_name, other = parse_uri(path)
  parent = None
  if directory_name == "":
    if path.lower() == ABFS_ROOT_S:
      return ABFS_ROOT_S
    return ABFS_ROOT
  else:
    parent = '/'.join(directory_name.split('/')[:-1])
  if path.lower().startswith(ABFS_ROOT):
    return normpath(ABFS_ROOT + filesystem + '/' + parent)
  return normpath(ABFS_ROOT_S + filesystem + '/' + parent)

def join(first,*complist):
  """
  Join a path on to another path
  """
  def _prep(uri):
    try:
      return '/%s/%s' % parse_uri(uri)[:2]
    except ValueError:
      return '/' if is_root(uri) else uri
  listings = [first]
  listings.extend(complist)
  joined = posixpath.join(*list(map(_prep, listings)))
  if joined and joined[0] == '/':
    if first.startswith(ABFS_ROOT_S):
      joined = 'abfss:/%s' % joined
    else:
      joined = 'abfs:/%s' % joined
  return joined


def abfspath(path, fs_defaultfs = None):
  """
  Converts a path to a path that the ABFS driver can use
  """
  if fs_defaultfs is None:
    try:
      fs_defaultfs = get_default_abfs_fs()
    except:
      LOG.warn("Configuration for ABFS is not set, may run into errors")
      return path
  filesystem, dir_name = ("","")
  try:
    filesystem, dir_name = parse_uri(path)[:2]
  except:
    return path
  account_name = ABFSACCOUNT_NAME.match(fs_defaultfs)
  LOG.debug("%s" % fs_defaultfs)
  if account_name:
    if path.lower().startswith(ABFS_ROOT):
      path = ABFS_ROOT + filesystem + account_name.group(1) + '/' + dir_name
    else:
      path = ABFS_ROOT_S + filesystem + account_name.group(1) + '/' + dir_name
  LOG.debug("%s" % path)
  return path

def abfsdatetime_to_timestamp(datetime):
  """
  Returns timestamp (seconds) by datetime string from ABFS API responses.
  ABFS REST API returns one types of datetime strings:
  * `Thu, 26 Feb 2015 20:42:07 GMT` for Object HEAD requests
    (see http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectHEAD.html);
  """
  # There is chance (depends on platform) to get
  # `'z' is a bad directive in format ...` error (see https://bugs.python.org/issue6641),
  #LOG.debug("%s" %datetime)
  stripped = time.strptime(datetime[:-4], '%a, %d %b %Y %H:%M:%S')
  assert datetime[-4:] == ' GMT', 'Time [%s] is not in GMT.' % datetime
  return int(calendar.timegm(stripped))
