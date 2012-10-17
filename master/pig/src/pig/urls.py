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

urlpatterns = patterns('pig.views',  
    url(r'delete/(?P<obj_id>\d+)/$', 'delete', name='delete'),
    url(r'clone/(?P<obj_id>\d+)/$', 'script_clone', name='clone'),
    url(r'piggybank/(?P<obj_id>\d+)/$', 'piggybank', name='piggybank'),
    url(r'piggybank/new/$', 'piggybank', name='piggybank_new'),
    url(r'piggybank_index/$', 'piggybank_index', name='piggybank_index'),
    url(r'udf_del/(?P<obj_id>\d+)/$', 'udf_del', name='udf_del'), 
    
    url(r'start_job/$', 'start_job', name="start_job"),
    url(r'kill_job/$', 'kill_job', name='kill_job'),
    url(r'get_job_result/$', 'get_job_result', name='get_job_result'),
    url(r'query_history/$', 'query_history', name='query_history'),
    url(r'notify/(?P<job_id>\w+)/$', 'notify_job_complited', name='notify_job_complited'),
    url(r'show_job_result/(?P<job_id>\w+)/$', 'show_job_result', name='show_job_result'),
    url(r'delete_job/(?P<job_id>\w+)/$', 'delete_job_object', name='delete_job_object'),
    url('(?P<obj_id>\d+)?/', 'index', name="view_script"),
    url(r'$', 'index', name='root_pig'),
)
