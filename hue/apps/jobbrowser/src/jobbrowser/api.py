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

from desktop.lib.paginator import Paginator
from django.utils.functional import wraps
from hadoop import cluster

import hadoop.yarn.history_server_api as history_server_api
import hadoop.yarn.mapreduce_api as mapreduce_api
import hadoop.yarn.resource_manager_api as resource_manager_api
import hadoop.yarn.node_manager_api as node_manager_api

from jobbrowser.conf import SHARE_JOBS
from jobbrowser.yarn_models import Application, Job as YarnJob, KilledJob as KilledYarnJob, Container
from hadoop.cluster import get_next_ha_yarncluster
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)

_DEFAULT_OBJ_PER_PAGINATION = 10


def get_api(user, jt):
  return YarnApi(user)


def rm_ha(funct):
  """
  Support RM HA by trying other RM API.
  """
  def decorate(api, *args, **kwargs):
    try:
      return funct(api, *args, **kwargs)
    except Exception, ex:
      if 'Connection refused' in str(ex):
        LOG.info('JobTracker not available, trying JT plugin HA: %s.' % ex)
        rm_ha = get_next_ha_yarncluster()
        if rm_ha is not None:
          config, api.resource_manager_api = rm_ha
          return funct(api, *args, **kwargs)
      raise ex
  return wraps(funct)(decorate)

class JobBrowserApi(object):

  def paginate_task(self, task_list, pagenum):
    paginator = Paginator(task_list, _DEFAULT_OBJ_PER_PAGINATION)
    return paginator.page(pagenum)


class YarnApi(JobBrowserApi):
  """
  List all the jobs with Resource Manager API.
  Get running single job information with MapReduce API.
  Get finished single job information with History Server API.

  The trick is that we use appid when the job is running and jobid when it is finished.
  We also suppose that each app id has only one MR job id.
  e.g. job_1355791146953_0105, application_1355791146953_0105

  A better alternative might be to call the Resource Manager instead of relying on the type of job id.
  The perfect solution would be to have all this logic embedded
  """
  def __init__(self, user):
    self.user = user
    self.resource_manager_api = resource_manager_api.get_resource_manager()
    self.mapreduce_api = mapreduce_api.get_mapreduce_api()
    self.history_server_api = history_server_api.get_history_server_api()

  def get_job_link(self, job_id):
    return self.get_job(job_id)

  @rm_ha
  def get_jobs(self, user, **kwargs):
    state_filters = {'running': 'UNDEFINED', 'completed': 'SUCCEEDED', 'failed': 'FAILED', 'killed': 'KILLED', }
    filters = {}

    if kwargs['username']:
      filters['user'] = kwargs['username']
    if kwargs['state'] and kwargs['state'] != 'all':
      filters['finalStatus'] = state_filters[kwargs['state']]

    json = self.resource_manager_api.apps(**filters)
    if type(json) == str and 'This is standby RM' in json:
      raise Exception(json)
    if json['apps']:
      jobs = [Application(app) for app in json['apps']['app']]
    else:
      return []

    if kwargs['text']:
      text = kwargs['text'].lower()
      jobs = filter(lambda job:
                    text in job.name.lower() or
                    text in job.id.lower() or
                    text in job.user.lower() or
                    text in job.queue.lower(), jobs)

    return self.filter_jobs(user, jobs)

  def filter_jobs(self, user, jobs, **kwargs):
    check_permission = not SHARE_JOBS.get() and not user.is_superuser

    return filter(lambda job:
                  not check_permission or
                  user.is_superuser or
                  job.user == user.username, jobs)

  @rm_ha
  def get_job(self, jobid):
    try:
      # App id
      jobid = jobid.replace('job', 'application')
      job = self.resource_manager_api.app(jobid)['app']

      if job['state'] == 'ACCEPTED':
        raise ApplicationNotRunning(jobid, job)
      elif job['state'] == 'KILLED':
        return KilledYarnJob(self.resource_manager_api, job)

      # MR id, assume 'applicationType': 'MAPREDUCE'
      jobid = jobid.replace('application', 'job')

      if job['state'] in ('NEW', 'SUBMITTED', 'ACCEPTED', 'RUNNING'):
        json = self.mapreduce_api.job(self.user, jobid)
        job = YarnJob(self.mapreduce_api, json['job'])
      else:
        json = self.history_server_api.job(self.user, jobid)
        job = YarnJob(self.history_server_api, json['job'])
    except ApplicationNotRunning, e:
      raise e
    except Exception, e:
      raise PopupException('Job %s could not be found: %s' % (jobid, e), detail=e)

    return job

  def get_tasks(self, jobid, **filters):
    filters.pop('pagenum')
    return self.get_job(jobid).filter_tasks(**filters)

  def get_task(self, jobid, task_id):
    return self.get_job(jobid).task(task_id)

  def get_tracker(self, container_id):
    return Container(self.node_manager_api.container(container_id))

class ApplicationNotRunning(Exception):

  def __init__(self, application_id, job):
    self.application_id = application_id
    self.job = job
