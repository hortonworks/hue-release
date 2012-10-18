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

from tempfile import NamedTemporaryFile
import os
from time import time
from templeton import Templeton
from subprocess import Popen, PIPE
import urllib2
import urllib
import httplib

from desktop.lib.exceptions import PopupException

import logging

LOG = logging.getLogger(__name__)

def hcat_client():
    class HCatClient(Templeton):
    
        def get_databases(self):
            """
            List the databases.
            """
            return self.get("ddl/database")['databases']
        
        
        def get_tables(self, db="default"):
            """
            List the tables.
            """
            return (self.get("ddl/database/%s/table" % db)['tables'], False, 'no errors')
        
        
        def get_columns(self, table, db="default"):
            """
            List the columns for the given table.
            """
            columns = []
            try:
                return self.get("ddl/database/%s/table/%s/column" % (db, table))['columns']
            except Exception:
                import traceback
                error = traceback.format_exc()
                raise PopupException('templeton hcatalog', title="templeton hcatalog", detail=error)
            return columns 
        
        
        def get_partitions(self, table, db="default"):
            """
            List the partitions for the given table.
            """
            partitions = []
            try:
                return self.get("ddl/database/%s/table/%s/partition" % (db, table))['partitions']
            except Exception:
                import traceback
                error = traceback.format_exc()
                raise PopupException('templeton hcatalog', title="templeton hcatalog", detail=error)
            return partitions
        
        
        def describe_table_extended(self, table, db="default"):
            """
            Describe the given table.
            """
            # response example:
            # {"minFileSize":0,"totalNumberFiles":0,"location":"hdfs://ip-10-191-121-144.ec2.internal:8020/apps/hive/warehouse/a002",
            # "lastUpdateTime":1350475455179,"outputFormat":"org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
            # "lastAccessTime":0,"columns":[{"name":"a","type":"string"}],
            # "partitionColumns":[{"name":"p","type":"string"}],"maxFileSize":0,"partitioned":true,
            # "owner":"root","inputFormat":"org.apache.hadoop.mapred.TextInputFormat","totalFileSize":0,
            # "database":"default","table":"a002","group":"hdfs","permission":"rwx------"}
            result = {}
            data = {'format':'extended'}
            resp = self.get("ddl/database/%s/table/%s" % (db, table), data)
            try:
                result['columns'] = resp['columns']
            except:
                raise Exception("""Could not get table description""")
            try:
                result['partitionColumns'] = resp['partitionColumns']
            except:
                result['partitionColumns'] = []
            return result
    
    
        def drop_table(self, table, db="default"):
            """
            Drop a table.
            """
            try:
                resp = self.delete("ddl/database/%s/table/%s" % (db, table))
            except Exception:
                import traceback
                error = traceback.format_exc()
                LOG.error(error)
                raise PopupException('templeton hcatalog', title="templeton hcatalog", detail=error)
            
            # handling templeton errors
            isError = False
            error = ''
            try: 
                error = resp['error']
                LOG.error(error)
                isError = True
            except KeyError:
                pass
            return (isError, error)         


        def create_table(self, dbname, query):
            # create tmp file
            tmp_file_name = '/tmp/create_table_%d.hcat' % (int(time()))
            query_file = open(tmp_file_name, "w")
            query_file.writelines(query)
            query_file.close()
 
            # execute command
            res, isError, error = self.hcat_cli(file=tmp_file_name)
    
            # remove tmp file
            if os.path.exists(query_file.name):
                os.remove(query_file.name)
            LOG.error(error)
            
            return (res, isError, error)
        
        
        def hcat_cli(self, execute=None, file=None):
            if not any([execute, file]):
                raise Exception("""One of either "execute" or "file" is required""")
            if execute:
                p = Popen("hcat -e '" + execute + "'", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            if file:
                p = Popen("hcat -f " + file, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            answer, error = p.communicate()
            LOG.error(error)
            return (answer, not answer, error)
        
        
        def hive_cli(self, execute=None, file=None):
            if not any([execute, file]):
                raise PopupException('hive cli error', title="hive cli error", detail="""One of either "execute" or "file" is required""")
            if execute:
                p = Popen("hive -e '" + execute + "'", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            if file:
                p = Popen("hive -f " + file, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            answer, error = p.communicate()
            LOG.error(error)
            return (answer, not answer, error)
        
    return HCatClient()
