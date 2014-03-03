## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
  'pig.views',
  url(r'delete/(?P<obj_id>\d+)/$', 'delete', name='delete'),
  url(r'^clone/(?P<obj_id>\d+)/$', 'script_clone', name='clone'),
  url(r'udf/new/$', 'udf_create', name='udf_new'),
  url(r'udf/del/(?P<obj_id>\d+)?/$', 'udf_delete', name='udf_delete'),
  url(r'udf/get/$', 'udf_get', name='udf_get'),
  url(r"download_job_result/(?P<job_id>\w+)/$", "download_job_result", name="download_job_result"),
  url(r'start_job/$', 'start_job', name="start_job"),
  url(r'kill_job/$', 'kill_job', name='kill_job'),
  url(r'get_job_result/$', 'get_job_result', name='get_job_result'),
  url(r'get_job_result_stdout/$', 'get_job_result_stdout', name='get_job_result_stdout'),
  url(r'get_job_result_stderr/$', 'get_job_result_stderr', name='get_job_result_stderr'),
  url(r'get_job_result_script/$', 'get_job_result_script', name='get_job_result_script'),
  url(r'query_history_job_detail/(?P<job_id>\w+)/$', 'query_history_job_detail', name='query_history_job_detail'),
  url(r'query_history/$', 'query_history', name='query_history'),
  url(r'autosave_scripts/$', 'autosave_scripts', name='autosave_scripts'),
  url(r'notify/(?P<job_id>\w+)/$', 'notify_job_completed', name='notify_job_completed'),
  url(r'show_job_result/(?P<job_id>\w+)/$', 'show_job_result', name='show_job_result'),
  url(r'delete_job/$', 'delete_job_object', name='delete_job_object'),
  url(r'ping_job/(?P<job_id>\w+)/$', 'ping_job', name='ping_job'),
  url(r'check_running_job/(?P<job_id>\w+)/$', 'check_running_job', name='check_running_job'),
  url(r'(?P<obj_id>\d+)?/', 'index', name="view_script"),
  url(r'check_script_title', 'check_script_title', name='check_script_title'),
  url(r'$', 'index', name='root_pig'),
)
