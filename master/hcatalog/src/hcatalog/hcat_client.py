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

from command import Command
from tempfile import NamedTemporaryFile
import os
from time import time

class HCatClient(Command):

    def get_tables(self, dbname, tbl_name):
        result = []
        isError = False
        error   = "No errors"
        
        # execute command
        command = Command()
        ret = command.execute('SHOW TABLES')
        if ret != False:
            result = ret.splitlines()
        else:
            isError = True
            error = command.last_error
            
        return (result, isError, error)
       
    def create_table(self, dbname, query):
        result = []
        isError = False
        error   = "No errors"
        
        # create tmp file
        #query_file = NamedTemporaryFile()
        tmp_file_name = '/tmp/create_table_%d.hcat' % (int(time()))
        query_file = open(tmp_file_name, "w")
        query_file.writelines(query)
        query_file.close()
 
        # execute command
        command = Command()
        ret = command.executeFromFile(query_file.name)
        if ret != False:
            result = ret.splitlines()
        else:
            isError = True
            error = command.last_error
         
        # remove tmp file
        os.remove(query_file.name)
        #if os.path.exists(query_file.name):
        #    os.unlink(query_file.name)
            
        return (result, isError, error)
