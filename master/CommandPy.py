from subprocess import Popen, PIPE

class CommandPy:

    file_path = ''
    shell_path = ''
    last_error = ''
    separator = '\r\n'

    def __init__(self, shell_path):
        self.shell_path = shell_path.split()
        self.file_path = self.shell_path[-1]

    def returnCode(self, code = ''):
        if code:
            self.command(code)
        slave = Popen(self.shell_path, stdin=PIPE, stdout=PIPE,
                      stderr=PIPE, close_fds = True)
        answer, error = slave.communicate()
        error = '\n'.join(filter(lambda x: '[main] INFO' not in x and
                                           '[main] WARN' not in x,
                                           error.split('\n')))
        if not answer:
            self.last_error = error
            return False
        else:
            return answer

    def command(self, command):
        fl = open(self.file_path, 'a')
        #fl.writelines(self.separator)
        fl.writelines(command)
        fl.close()

