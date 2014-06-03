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

import time
from pig.templeton import Templeton

from datetime import datetime
import simplejson as json
import logging

LOG = logging.getLogger("analitics")


class HCatClient(Templeton):
    def __init__(self, user="sandbox"):
        super(HCatClient, self).__init__(user)

    def get_databases(self, like="*"):
        """
        List the databases.
        """
        data = {'like': like}
        try:
            return self.get("ddl/database", data)['databases']
        except Exception as ex:
            error = """HCatClient: error on getting a database list: %s""" % unicode(ex)
            LOG.exception(error)
            raise Exception(error)

    def create_database(self, database, group=None, permissions=None, location=None, comment=None, properties=None):
        """
        Create database.
        """
        LOG.info('HCatalog client, creating database \'%s\'' % (database))
        resp = {}
        data = {}
        data['group'] = group
        data['permissions'] = permissions
        data['location'] = location
        data['comment'] = comment
        data['properties'] = properties
        try:
            resp = self.put('ddl/database/%s' % database, data=json.dumps(data))
            if not ('database' in resp and resp['database'] == database):
                LOG.warning('HCatClient error on create database: internal error')
            if 'error' in resp:
                LOG.error(resp['error'])
                raise Exception('HCatClient error on create table: %s' % (resp['error']))
        except Exception as ex:
            LOG.exception(unicode(ex))
            raise Exception('HCatClient error on create database: %s' % unicode(ex))

    def drop_database(self, database, if_exists=False, option=None, group=None, permissions=None):
        """
        Drop a database.
        """
        params = {}
        params['ifExists'] = if_exists
        if option is not None:
            params['option'] = option
        if group is not None:
            params['group'] = group
        if permissions is not None:
            params['permissions'] = permissions
        try:
            resp = self.delete("ddl/database/%s" % database, params=params)
            if not ('database' in resp and resp['database'] == database):
                LOG.warning('HCatClient error on deleting database: internal error')
            if 'error' in resp:
                LOG.error(resp['error'])
                raise Exception('HCatClient error on deleting database: %s' % (resp['error']))
        except Exception as ex:
            error = """HCatClient: error on delete database: %s""" % unicode(ex)
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

    def create_table(self, dbname, table, query):
        """
        Create table.
        """
        LOG.info('HCatalog client, create table query:\n%s' % (query))
        resp = {}
        try:
            resp = self.put('ddl/database/%s/table/%s' % (dbname, table), data=query)
        except Exception as ex:
            LOG.exception(unicode(ex))
            raise Exception('HCatClient error on create table: %s' % unicode(ex))
        try:
            error = resp['error']
            exec_error = ''
            if 'exec' in resp and 'stderr' in resp['exec']:
                exec_error = '\n%s' % resp['exec']['stderr']
            LOG.error(error)
            raise Exception('HCatClient error on create table: %s%s' % (error, exec_error))
        except KeyError:
            pass

    def do_hive_query_and_wait(self, hive_file=None, execute=None, timeout_sec=1000.0):
        SLEEP_INTERVAL = 1.0
        statusdir = "/tmp/.hivejobs/%s" % datetime.now().strftime("%s")
        job = self.hive_query(hive_file=hive_file, execute=execute, statusdir=statusdir)
        curr = time.time()
        end = curr + timeout_sec
        while curr <= end:
            try:
                result = self.check_job(job['id'])
                LOG.info(unicode(result))
            except Exception as ex:
                raise Exception("""HCatalog client, do_hive_query_and_wait error: %s""" % unicode(ex))
            if 'exitValue' in result and result['exitValue']:
                if 'status' in result and 'failureInfo' in result['status'] and result['status']['failureInfo'] != 'NA':
                    raise Exception(
                        """HCatalog client, do_hive_query_and_wait error: %s""" % unicode(result.status.failureInfo))
            if ('completed' in result and result['completed']) or \
                    ('status' in result and 'jobComplete' in result['status'] and result['status']['jobComplete']):
                return # success
            time.sleep(SLEEP_INTERVAL)
            curr = time.time()
        raise Exception("""HCatalog client, do_hive_query_and_wait error: %s""" % "Timeout occurred")

    def do_hive_query(self, hive_file=None, execute=None):
        statusdir = "/tmp/.hivejobs/%s" % datetime.now().strftime("%s")
        try:
            job = self.hive_query(hive_file=hive_file, execute=execute, statusdir=statusdir)
        except Exception as ex:
            LOG.exception(unicode(ex))
            raise Exception('HCatClient error executing hive query: %s' % unicode(ex))
        return job['id'] if 'id' in job else None
