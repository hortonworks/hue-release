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


class PigClient(object):

    file_path = ''
    shell_path = ''
    last_error = ''

    def __init__(self, shell_path, script_path, pig_src):
        self.shell_path = shell_path.split()
        self.file_path = script_path
        self.pig_src = pig_src

    def returnCode(self):
        self.createPigFile()
        slave = Popen(self.shell_path, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        slave.wait()
        answer, error = slave.stdout.read(), slave.stderr.read()
        if not answer:
            return error
        else:
            return answer

    def createPigFile(self):
        directory = os.path.dirname(self.file_path)
        try:
            os.stat(directory)
        except:
            os.mkdir(directory)
        f1 = open(self.file_path, 'w')
        f1.write(self.pig_src)
        f1.close()
