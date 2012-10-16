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

class CommandPy:

    file_path = ''
    shell_path = ''
    last_error = ''

    def __init__(self, shell_path):
        self.shell_path = shell_path.split()
        self.file_path = self.shell_path[-1]

    def returnCode(self):
        """
          This method return False if script return error
          If script return void answer, error write to last_error variable
          if script return answer, then method return this answer
        """
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

    def HDFS_command(self, *args):
        """ this method work with hdfs commands """
        default_command = ['hadoop', 'dfs']
        command_to_hdfs = default_command + list(args)
        hdfs = Popen(command_to_hdfs)

        if hdfs.returncode == 0:
            return True
        else:
            return False

    def copyToLocal(self, fromFile, toFile):
        """ Copy from hdfs to local """
        self.HDFS_command("-copyToLocal", fromFile, toFile)

    def copyFromLocal(self, fromFile, toFile):
        """ Copy from local to hdfs """
        self.HDFS_command("-copyFromLocal", fromFile, toFile)
