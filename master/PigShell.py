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

        fl = open(self.file_path, 'w')
        fl.write(''.join(code))
        fl.close()

        return returnCommand

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
