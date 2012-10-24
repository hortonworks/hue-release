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
from subprocess import Popen, PIPE
import os

def logs(returnCode):
    def wrappen(self):
        from time import strftime
        start_time = strftime("%Y-%m-%d %H:%M:%S")
        answer = returnCode(self)
        end_time = strftime("%Y-%m-%d %H:%M:%S")
        if not answer:
            status = '0'
            answer = self.last_error
        else:
            status = '1'
        if self.LogModel:
            log = self.LogModel(start_time = start_time,
                            end_time = end_time,
                            status = status,
                            script_name = self.file_path)
            log.save()
        return answer
    return wrappen

class CommandPy:

    file_path = ''
    shell_path = ''
    last_error = ''

    def __init__(self, shell_path, pig_src=None, LogModel=None):
        self.shell_path = shell_path.split()
        self.file_path = self.shell_path[-1]
        self.LogModel = LogModel
        self.pig_src = pig_src
    
    @logs
    def returnCode(self):
        self.create_pigscript_file()
        slave = Popen(self.shell_path, stdin=PIPE, stdout=PIPE,
                      stderr=PIPE, close_fds = True)
        slave.wait()
        answer, error = slave.stdout.read(), slave.stderr.read()
        error = '\n'.join(filter(lambda x: '] INFO' not in x and
                                           '] WARN' not in x,
                                           error.split('\n')))
        if not answer:
            self.last_error = error
            return False
        else:
            return answer

    def create_pigscript_file(self):
        directory = os.path.dirname(self.file_path)
        try:
            os.stat(directory)
        except:
            os.mkdir(directory)
        f1 = open(self.file_path, 'w')
        f1.write(self.pig_src)