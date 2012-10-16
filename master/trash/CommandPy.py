from subprocess import Popen, PIPE

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

    def __init__(self, shell_path, LogModel = None):
        self.shell_path = shell_path.split()
        self.file_path = self.shell_path[-1]
        self.LogModel = LogModel

    @logs
    def returnCode(self):

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
