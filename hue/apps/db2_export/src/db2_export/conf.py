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
"""Configuration options for Query Result Export (Beeswax)."""
from desktop.lib.conf import Config, ConfigSection, UnspecifiedConfigSection 
from db2_export.human_size import human_size
import re

def ucase(value):
  return value.upper()

EXPORT_LIMIT = Config(
    key="export_limit",
    help="Table/Query result export limit in bytes default: 100M",
    private=True,
    type = human_size,
    default="100MB")

HUE_ENV = Config(
    key = "hue_env",
    help = "The environment of HUE: DEV/TEST/PROD",
    private = True,
    type = ucase,
    default = "DEV")

DATABASES = UnspecifiedConfigSection(
    key = "databases",
    help = "The databases are supported for exporting",
    each = ConfigSection(members=dict(
      DEFAULT_SCHEMA = Config(key="default_schema",
        help = "The default schema of the databse for exporting",
        private = True),
      DEFAULT_TABLESPACE = Config(key="default_tablespace",
        help = "The default tablespace of the databse for exporting",
        private = True))) )

EXPORT_DBS = UnspecifiedConfigSection(
    key = "export_dbs",
    help = "The databases for exporting in different environments",
    each = ConfigSection(members=dict(
      DBS = Config(key="dbs",
        help = "Comma separated database names",
        private = True))))

def to_uppercase(conf):
  if isinstance(conf, dict):
    return dict([ (k.upper(), to_uppercase(v)) for (k,v) in conf.items() ])
  elif isinstance(conf, list):
    return [ to_uppercase(v) for v in conf ]
  elif isinstance(conf, basestring):
    return conf.upper()

def normalize_export_dbs(conf):
  return to_uppercase(dict([(k, v["dbs"]) for k,v in conf.items()]))
