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

import os
from time import time
from pig.templeton import Templeton
from subprocess import Popen, PIPE

import simplejson as json

import logging

LOG = logging.getLogger("analitics")


class HCatClient(Templeton):

    def get_databases(self):
        """
        List the databases.
        """
        try:
            return self.get("ddl/database")['databases']
        except Exception as ex:
            error = """HCatClient: error on getting a database list: %s""" % unicode(ex)
            LOG.exception(error)
            raise Exception(error)

    def get_tables(self, db="default"):
        """
        List the tables.
        """
        try:
            return self.get("ddl/database/%s/table" % db)['tables']
        except Exception as ex:
            error = """HCatClient: error on getting a table list: %s""" % unicode(ex)
            LOG.exception(error)
            raise Exception(error)

    def get_columns(self, table, db="default"):
        """
        List the columns for the given table.
        """
        columns = []
        try:
            return self.get("ddl/database/%s/table/%s/column" % (db, table))['columns']
        except Exception as ex:
            error = """HCatClient: error on getting a column list: %s""" % unicode(ex)
            LOG.exception(error)
            raise Exception(error)
        return columns

    def get_partitions(self, table, db="default"):
        """
        List the partitions for the given table.
        """
        partitions = []
        try:
            return self.get("ddl/database/%s/table/%s/partition" % (db, table))['partitions']
        except Exception as ex:
            error = """HCatClient: error on getting partitions: %s""" % unicode(ex)
            LOG.exception(error)
            raise Exception(error)
        return partitions

    def describe_table_extended(self, table, db="default"):
        """
        Describe the given table.
        """
        result = {}
        data = {'format': 'extended'}
        resp = {}
        try:
            resp = self.get("ddl/database/%s/table/%s" % (db, table), data)
            result['columns'] = resp['columns']
            result['partitioned'] = resp['partitioned']
        except Exception as ex:
            error = """Could not get table description (extended): %s""" % unicode(ex)
            LOG.exception(error)
            raise Exception(error)
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
        data = {'format': 'extended'}
        try:
            resp = self.delete("ddl/database/%s/table/%s" % (db, table))
        except Exception as ex:
            error = """HCatClient: error on table delete query: %s""" % unicode(ex)
            LOG.exception(error)
            raise Exception(error)

            # handling templeton errors
            try:
                error = """HCatClient: error on dropping table: %s""" % unicode(resp['error'])
                LOG.error(error)
                raise Exception(error)

            except KeyError:
                pass

    def describe_partition(self, table, partition, db="default"):
        """
        Describe a partition.
        """
        resp = self.get("ddl/database/%s/table/%s/partition/%s" % (db, table, partition))
        # validating response
        try:
            error = """HCatClient: error on describing partition: %s""" % unicode(resp['error'])
            LOG.error(error)
            raise Exception(error)
        except KeyError:
            pass
        return resp

    def drop_partition(self, table, partition, db="default"):
        """
        Drop a partition.
        """
        try:
            resp = self.delete("ddl/database/%s/table/%s/partition/%s" % (db, table, partition))
        except Exception as ex:
            error = """HCatClient: error on dropping partitions: %s""" % unicode(ex)
            LOG.exception(error)
            raise Exception(error)
        try:
            error = """HCatClient: error on dropping partition: %s""" % unicode(resp['error'])
            LOG.error(error)
            raise Exception(error)
        except KeyError:
            pass

    def get_partition_location(self, table, partition, db="default"):
        try:
            return self.describe_partition(table, partition, db)['location']
        except KeyError:
            raise Exception("""HCatClient: error on getting partition location: attribute is missed in a response""")

    def create_table(self, dbname, query):
        try:
            LOG.info("HCatalog client, create table query:\n%s" % (query))
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
        except Exception as ex:
            error = """HCatalog cli: error on creating table: %s""" % unicode(ex)
            LOG.exception(error)
            raise Exception(error)

    def create_table_by_templeton(self, dbname, table, query):
        """
        Create table.
        """
        LOG.info("HCatalog client, create table query:\n%s" % (query))
        headers = {'content-type': 'application/json'}
        resp = {}
        try:
            resp = self.put("ddl/database/%s/table/%s" % (dbname, table), data=query, headers=headers).json()
        except Exception as ex:
            LOG.exception(unicode(ex))
            raise Exception("HCatClient error on create table: %s" % unicode(ex))
        try:
            error = resp['error']
            LOG.error(error)
            raise Exception("HCatClient error on create table: %s" % error)
        except KeyError:
            pass

    def hcat_cli(self, execute=None, file=None):
        if not any([execute, file]):
            raise Exception("""One of either "execute" or "file" is required""")
        if execute:
            p = Popen("hcat -e '" + execute + "'", shell=True,
                      stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        if file:
            p = Popen("hcat -f " + file, shell=True,
                      stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        answer, error = p.communicate()
        LOG.error(error)
        return (answer, not answer, error)

    def hive_cli(self, execute=None, file=None):
        if not any([execute, file]):
            raise Exception('hive cli error: one of either "execute" or "file" is required')
        if execute:
            p = Popen("hive -e '" + execute + "'", shell=True,
                      stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        if file:
            p = Popen("hive -f " + file, shell=True,
                      stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        answer, error = p.communicate()
        LOG.error(error)
        return (answer, not answer, error)


CLIENT = HCatClient()


def hcat_client():
    return CLIENT
