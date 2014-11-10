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

import os
import logging

from hadoop import conf
from hadoop.fs import webhdfs, LocalSubFileSystem

from desktop.lib.paths import get_build_dir


LOG = logging.getLogger(__name__)


FS_CACHE = None
MR_CACHE = None
MR_NAME_CACHE = 'default'


def _make_filesystem(identifier):
  choice = os.getenv("FB_FS")

  if choice == "testing":
    path = os.path.join(get_build_dir(), "fs")
    if not os.path.isdir(path):
      LOG.warning(("Could not find fs directory: %s. Perhaps you need to run manage.py filebrowser_test_setup?") % path)
    return LocalSubFileSystem(path)
  else:
    cluster_conf = conf.HDFS_CLUSTERS[identifier]
    return webhdfs.WebHdfs.from_config(cluster_conf)

def get_hdfs(identifier="default"):
  global FS_CACHE
  get_all_hdfs()
  return FS_CACHE[identifier]


def get_all_hdfs():
  global FS_CACHE
  if FS_CACHE is not None:
    return FS_CACHE

  FS_CACHE = {}
  for identifier in conf.HDFS_CLUSTERS.keys():
    FS_CACHE[identifier] = _make_filesystem(identifier)
  return FS_CACHE


def get_default_yarncluster():
  """
  Get the default RM (not necessarily HA).
  """
  global MR_NAME_CACHE

  try:
    return conf.YARN_CLUSTERS[MR_NAME_CACHE]
  except KeyError:
    return get_yarn()


def get_yarn():
  global MR_NAME_CACHE
  if MR_NAME_CACHE in conf.YARN_CLUSTERS and conf.YARN_CLUSTERS[MR_NAME_CACHE].SUBMIT_TO.get():
    return conf.YARN_CLUSTERS[MR_NAME_CACHE]

  for name in conf.YARN_CLUSTERS.keys():
    yarn = conf.YARN_CLUSTERS[name]
    if yarn.SUBMIT_TO.get():
      return yarn


def get_next_ha_yarncluster():
  """
  Return the next available YARN RM instance and cache its name.
  """
  from hadoop.yarn.resource_manager_api import ResourceManagerApi
  global MR_NAME_CACHE

  has_ha = sum([conf.YARN_CLUSTERS[name].SUBMIT_TO.get() for name in conf.YARN_CLUSTERS.keys()]) >= 2

  for name in conf.YARN_CLUSTERS.keys():
    config = conf.YARN_CLUSTERS[name]
    if config.SUBMIT_TO.get():
      rm = ResourceManagerApi(config.RESOURCE_MANAGER_API_URL.get(), config.SECURITY_ENABLED.get())
      if has_ha:
        try:
          cluster_info = rm.cluster()
          if cluster_info['clusterInfo']['haState'] == 'ACTIVE':
            MR_NAME_CACHE = name
            LOG.warn('Picking RM HA: %s' % name)
            from hadoop.yarn import resource_manager_api
            resource_manager_api._api_cache = None # Reset cache
            return (config, rm)
          else:
            LOG.info('RM %s is not RUNNING, skipping it: %s' % (name, cluster_info))
        except Exception, ex:
          LOG.info('RM %s is not available, skipping it: %s' % (name, ex))
      else:
        return (config, rm)
  return None


def get_cluster_for_job_submission():
  """
  Check the 'submit_to' for each MR/Yarn cluster, and return the
  config section of first one that enables submission.

  Support Yarn HA.
  """
  yarn = get_next_ha_yarncluster()
  if yarn:
    return yarn

  return None


def get_cluster_conf_for_job_submission():
  cluster = get_cluster_for_job_submission()

  if cluster:
    config, rm = cluster
    return config
  else:
    return None


def get_cluster_addr_for_job_submission():
  """
  Check the 'submit_to' for each Yarn cluster, and return the logical name or host:port of first one that enables submission.
  """
  if is_yarn():
    if get_yarn().LOGICAL_NAME.get():
      return get_yarn().LOGICAL_NAME.get()

  conf = get_cluster_conf_for_job_submission()
  if conf is None:
    return None

  return conf.RESOURCE_MANAGER_RPC_URL.get()


def is_yarn():
  return get_yarn() is not None


def clear_caches():
  """
  Clears cluster's internal caches.  Returns
  something that can be given back to restore_caches.
  """
  global FS_CACHE, MR_CACHE
  old = FS_CACHE, MR_CACHE
  FS_CACHE, MR_CACHE = None, None
  return old


def restore_caches(old):
  """
  Restores caches from the result of a previous clear_caches call.
  """
  global FS_CACHE, MR_CACHE
  FS_CACHE, MR_CACHE = old
