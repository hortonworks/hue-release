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
    url(r'logs/$', 'show_logs', name='logs'),
    url(r'delete/(?P<obj_id>\d+)/$', 'delete', name='delete'),
    url(r'clone/(?P<obj_id>\d+)/$', 'script_clone', name='clone'),
    url(r'piggybank/(?P<obj_id>\d+)/$', 'piggybank', name='piggybank'),
    url(r'(?P<obj_id>\d+)/$', 'one_script', name='one_script'),
    url(r'new/$', 'new_script', name='new_script'),
    url(r'$', 'index', name='root_pig'),
)
