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
from CommandPy import CommandPy

class PigShell(CommandPy):

    def ShowCommands(self, command = 'EXPLAIN'):
        """
        This method get 1 parameter. (EXPLAIN or DESCRIBE)
        Return code with one of this commands
        return False - means that in file no variables
        """
        last_variable = self.getLastVariable()
        if not last_variable:
            return False
        fl = open(self.file_path, 'a+')
        code = fl.readlines()
        fl.writelines('%s %s;' % (command, last_variable))
        fl.close()

        returnCommand = self.returnCode()
        if returnCommand:
            if command.upper() == 'DESCRIBE':
                returnCommand = returnCommand.split('\n')[-1]
            elif command.upper() == 'EXPLAIN':
                returnCommand = '%s\n%s\n%s' % ('-' * 47, 'Logical Plan:',
                                                returnCommand.split('Logical Plan:')[1])
            elif command.upper() == 'DUMP':
                dump = returnCommand.split('\n')[::-1]
                i = 0
                for d in dump:
                    try:
                        if d[0] != '(' or d[-1] != ')':
                            break
                    except IndexError:
                        pass
                    i += 1
                returnCommand = dump[:i + 1][::-1]
            else:
                return False

        fl = open(self.file_path, 'w')
        fl.write(''.join(code))
        fl.close()

        return returnCommand

    def DUMPlimit(self):
        pass

    def getLastVariable(self):
        """
        This method find last declared variable in PIG file script
        """
        fl = open(self.file_path, 'r')
        code = fl.readlines()[::-1]
        last_variable = ''
        for c in code:
            try:
                variable_index = c.index('=')
                last_variable = c[:variable_index - 1].strip()
                break
            except ValueError:
                continue

        fl.close()

        return last_variable
