# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('hcatalog.views',
  url(r'^$', 'index', name='index'),
  url(r'^listdir/(?P<path>.*)$', 'listdir', name='listdir'),
  url(r'^databases/json$', 'list_databases_json', name='list_databases_json'),
  url(r'^databases$', 'show_databases', name='show_databases'),
  url(r'^database/drop$', 'drop_database', name='drop_database'),
  url(r'^database/create$', 'create_database', name='create_database'),
  url(r'^tables/(?P<database>\w+)?$', 'show_tables', name='show_tables'),
  url(r'^pig_view/(?P<database>\w+)/(?P<table>\w+)$', 'pig_view', name='pig_view'),
  url(r'^hive_view/(?P<database>\w+)/(?P<table>\w+)$', 'hive_view', name='hive_view'),
  url(r'^hive_view_download/(?P<id>\d+)/(?P<format>\w+)$', 'hive_view_download', name='download'),
  url(r'^execute/(?P<design_id>\d+)?$', 'execute_query', name='execute_query'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/describe$', 'describe_table', name='describe_table'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/json/$', 'describe_table_json', name='describe_table_json'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/load$', 'load_table', name='load_table'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/read$', 'read_table', name='read_table'),
  url(r'^table/(?P<database>\w+)?/drop$', 'drop_table', name='drop_table'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/browse_partition$', 'browse_partition', name='browse_partition'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/drop_partition$', 'drop_partition', name='drop_partition'),
  url(r'^tables/json/(?P<database>\w+)?$', 'list_tables_json', name='list_tables_json'),
  url(r'^watch/(?P<id>\d+)$', 'watch_query', name='watch_query'),
  url(r'^watch/(?P<id>\d+)/(?P<download_format>\w+)$', 'watch_query', name='watch_query'),
  url(r'^results/(?P<id>\d+)/(?P<first_row>\d+)$', 'view_results', name='view_results'),
  url(r'ping_hive_job/(?P<job_id>\w+)/$', 'ping_hive_job', name='ping_hive_job'),
)

urlpatterns += patterns(
  'hcatalog.create_table',
  url(r'^create/create_table/(?P<database>\w+)?$', 'create_table', name='create_table'),
)

urlpatterns += patterns(
    'hcatalog.file_import',
    url(r'^create/create_from_file/(?P<database>\w+)?$', 'create_from_file', name='create_from_file'),

    )