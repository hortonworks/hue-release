from CommandPy import CommandPy

class PigShell(CommandPy):

    commandOutput = ('DESCRIBE', 'EXPLAIN', 'DUMP',
                     'ILLUSTRATE', 'STORE', 'CAT')

    def ShowCommands(self, command = 'EXPLAIN'):
        """
          This method get 1 parameter. (EXPLAIN or DESCRIBE)
          Return code with one of this commands
          return False - means that in file no variables
        """
        last_variable = self.getLastVariable()
        if not last_variable:
            return False

        fl = open(self.file_path, 'r')
        code = self.validate(fl.readlines())
        fl.close()

        # Create temporary file
        file_name = self.createPigFile(self.file_path, code)
        self.shell_path = self.shell_path[:-1].append(file_name)

        returnCommand = self.returnCode()

        # delete temporary file
        self.deletePigFile(file_name)

        return returnCommand

    def validate(self, text):
        """
          This method delete all output command
          Return filter text
        """
        filterText = [t for t in text if t.split(' ')[0].upper() not in self.commandOutput]
        return '\n'.join(filterText)

    def createPigFile(self, name, text):
        """
          Create temporary pig script file
          Return temporary file name
        """
        from time import time
        file_name = self.file_path[:-4]
        new_file = '%s_%d.pig' % (file_name, int(time()))
        a = open(new_file, 'w')
        a.write(text)
        a.close()
        return new_file

    def deletePigFile(self, name):
        """
          Delete pig script file
        """
        from os import remove
        remove(name)

    def getLastVariable(self):
        """
          This method find last declared variable in PIG file script
        """
        fl = open(self.file_path, 'r')
        code = fl.readlines()[::-1]
        last_variable = ''
        for c in code:
            try:
                var_index = c.index('=')
                if c[var_index - 1] not in ['<', '!', '>'] and c[var_index + 1] not in ['=']:
                    last_variable = c[:var_index - 1].strip()
                    break
            except ValueError:
                continue

        fl.close()

        return last_variable
