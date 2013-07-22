#!/usr/bin/env python
# Licensed to Hortonworks, inc. under one
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

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('hbase.views',
  url(r'table/new$', 'create_table'),
  url(r'table/view/(?P<table>.+)$', 'view_table'),
  url(r'table/browse/(?P<table>.+)$', 'browse_data'),
  url(r'table/disable/(?P<table>.+)$', 'disable_table'),
  url(r'table/drop/(?P<table>.+)$', 'drop_table'),
  url(r'table/compact/(?P<table>.+)$', 'compact_table'),
  url(r'table/enable/(?P<table>.+)$', 'enable_table'),
  url(r'table/versions/json/(?P<table>\S+)/(?P<row>\S+)/(?P<column>\S+)$', 'get_versions_json'),
  url(r'table/data/json/(?P<table>.+)$', 'get_data_json'),
  url(r'tables/list/json$', 'table_list_json'),
  url(r'^$', 'index'),
)
