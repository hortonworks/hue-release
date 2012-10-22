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
            try:
                return self.get("ddl/database")['databases']
            except Exception, ex:
                raise Exception("""Templeton: error on getting a list of databases: %s""" % str(ex))

        
        def get_tables(self, db="default"):
            """
            List the tables.
            """
            try:
                return self.get("ddl/database/%s/table" % db)['tables']
            except Exception, ex:
                raise Exception("""Templeton: error on getting a list of tables: %s""" % str(ex))

         
        def get_columns(self, table, db="default"):
            """
            List the columns for the given table.
            """
            columns = []
            try:
                return self.get("ddl/database/%s/table/%s/column" % (db, table))['columns']
            except Exception, ex:
                raise Exception("""Templeton: error on getting a column list: %s""" % str(ex))
            return columns 
        
        
        def get_partitions(self, table, db="default"):
            """
            List the partitions for the given table.
            """
            partitions = []
            try:
                return self.get("ddl/database/%s/table/%s/partition" % (db, table))['partitions']
            except Exception, ex:
                raise Exception("""Templeton: error on getting partitions: %s""" % str(ex))
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
            resp = {}
            try:
                resp = self.get("ddl/database/%s/table/%s" % (db, table), data)
                result['columns'] = resp['columns']
                result['partitioned'] = resp['partitioned']
            except Exception, ex:
                raise Exception("""Could not get table description (extended): %s""" % str(ex))
            try:
                if result['partitioned']:
                    result['partitionColumns'] = resp['partitionColumns']
            except:
                result['partitioned'] = False
                result['partitionColumns'] = []
            return result
    
    
        def drop_table(self, table, db="default"):
            """
            Drop a table.
            """
            try:
                resp = self.delete("ddl/database/%s/table/%s" % (db, table))
            except Exception, ex:
                import traceback
                error = traceback.format_exc()
                LOG.error(error)
                raise Exception("""Templeton: error on getting partitions: %s""" % str(ex))           
            
            # handling templeton errors
            try: 
                error = resp['error']
                LOG.error(error)
                raise Exception("""Templeton: error on dropping table: %s""" % str(ex))
            except KeyError:
                pass
 
 
        def describe_partition(self, table, partition, db="default"):
            """
            Describe a partition.
            """
            # response example:
            # {"minFileSize":60,"totalNumberFiles":1,
            # "location":"hdfs://ip-10-191-121-144.ec2.internal:8020/apps/hive/warehouse/a002/p11=bbb/p22=b",
            # "lastUpdateTime":1350651963556,
            # "outputFormat":"org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
            # "lastAccessTime":1350440595100,"columns":[{"name":"a","type":"string"}],
            # "partitionColumns":[{"name":"p11","type":"string"},{"name":"p22","type":"string"}],
            # "maxFileSize":60,"partitioned":true,
            # "owner":"root","inputFormat":"org.apache.hadoop.mapred.TextInputFormat","totalFileSize":60,
            # "database":"default","table":"a002","partition":"p11='bbb',p22='b'"}
            resp = self.get("ddl/database/%s/table/%s/partition/%s" % (db, table, partition))
            # validating response
            try: 
                error = resp['error']
                LOG.error(error)
                raise Exception("""Templeton: error on describing partition: %s""" % error)
            except KeyError:
                pass
            return resp        
        

        def drop_partition(self, table, partition, db="default"):
            """
            Drop a partition.
            """
            try:
                resp = self.delete("ddl/database/%s/table/%s/partition/%s" % (db, table, partition))
            except Exception, ex:
                raise Exception("""Templeton: error on dropping partitions: %s""" % str(ex))
            try: 
                error = resp['error']
                LOG.error(error)
                raise Exception("""Templeton: error on dropping partition: %s""" % error)
            except KeyError:
                pass


        def get_partition_location(self, table, partition, db="default"):
            try: 
                return self.describe_partition(table, partition, db)['location']
            except KeyError:
                raise Exception("""Templeton: error on getting partition location: attribute is missed in a response""")


        def create_table(self, dbname, query):
            try:
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
                if isError:
                    LOG.error(error)
            except Exception, ex:
                raise Exception("""HCatalog cli: error on creating table: %s""" % str(ex))
        
        
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
