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

"""
Utils for interacting with HCatalog
"""

import logging
import time

import desktop.conf
import hadoop.cluster

from django.utils.encoding import smart_str, force_unicode
from desktop.lib import thrift_util

from hcatalog.hcat_client import HCatClient

LOG = logging.getLogger(__name__)

def meta_client():
  """Get the hcatalog client to talk to the metastore"""

  class UnicodeMetastoreClient(object):
    """Wrap the hcatalog client to take and return Unicode."""
    def __init__(self, client):
      self._client = client

    def __getattr__(self, attr):
      if attr in self.__dict__:
        return self.__dict__[attr]
      return getattr(self._client, attr)

    def _encode_storage_descriptor(self, sd):
      _encode_struct_attr(sd, 'location')
      for col in sd.cols:
        _encode_struct_attr(col, 'comment')
      self._encode_map(sd.parameters)

    def _decode_storage_descriptor(self, sd):
      _decode_struct_attr(sd, 'location')
      for col in sd.cols:
        _decode_struct_attr(col, 'comment')
      self._decode_map(sd.parameters)

    def _encode_map(self, mapp):
      for key, value in mapp.iteritems():
        mapp[key] = smart_str(value, strings_only=True)

    def _decode_map(self, mapp):
      for key, value in mapp.iteritems():
        mapp[key] = force_unicode(value, strings_only=True, errors='replace')

    def create_database(self, name, description):
      description = smart_str(description)
      return self._client.create_database(name, description)

    def get_database(self, *args, **kwargs):
      db = self._client.get_database(*args, **kwargs)
      return _decode_struct_attr(db, 'description')

    def get_fields(self, *args, **kwargs):
      res = self._client.get_fields(*args, **kwargs)
      for fschema in res:
        _decode_struct_attr(fschema, 'comment')
      return res
  
    def get_tables(self, dbname, tbl_name):
      tables, isError, error = self._client.get_tables(dbname, tbl_name)
      #self._decode_storage_descriptor(res.sd)
      #self._decode_map(res.parameters)
      return (tables, isError, error)  

    def get_table(self, *args, **kwargs):
      res = self._client.get_table(*args, **kwargs)
      self._decode_storage_descriptor(res.sd)
      self._decode_map(res.parameters)
      return res

    def alter_table(self, dbname, tbl_name, new_tbl):
      self._encode_storage_descriptor(new_tbl.sd)
      self._encode_map(new_tbl.parameters)
      return self._client.alter_table(dbname, tbl_name, new_tbl)

    def _encode_partition(self, part):
      self._encode_storage_descriptor(part.sd)
      self._encode_map(part.parameters)
      return part

    def _decode_partition(self, part):
      self._decode_storage_descriptor(part.sd)
      self._decode_map(part.parameters)
      return part

    def add_partition(self, new_part):
      self._encode_partition(new_part)
      part = self._client.add_partition(new_part)
      return self._decode_partition(part)

    def get_partition(self, *args, **kwargs):
      part = self._client.get_partition(*args, **kwargs)
      return self._decode_partition(part)

    def get_partitions(self, *args, **kwargs):
      part_list = self._client.get_partitions(*args, **kwargs)
      for part in part_list:
        self._decode_partition(part)
      return part_list

    def alter_partition(self, db_name, tbl_name, new_part):
      self._encode_partition(new_part)
      return self._client.alter_partition(db_name, tbl_name, new_part)

  client = HCatClient()
  return UnicodeMetastoreClient(client)


def _decode_struct_attr(struct, attr):
  try:
    val = getattr(struct, attr)
  except AttributeError:
    return struct
  unival = force_unicode(val, strings_only=True, errors='replace')
  setattr(struct, attr, unival)
  return struct

def _encode_struct_attr(struct, attr):
  try:
    unival = getattr(struct, attr)
  except AttributeError:
    return struct
  val = smart_str(unival, strings_only=True)
  setattr(struct, attr, val)
  return struct
