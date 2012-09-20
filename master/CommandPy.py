from subprocess import Popen, PIPE#, STDOUT

#RUBY_SHELL_PATH = 'C:/Ruby193/bin/ruby C:/Users/Yuri/Dropbox/Programming/Python/Ruby_Python/slave.rb'
PIG_LATIN_SHELL = 'pig -x local pig.pig'

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
        slave = Popen(self.shell_path, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds = True)
        answer = slave.communicate()
        if not answer[1]:
            return answer[0]#.split(self.separator)\
        else:
            self.last_error = answer[1]
            return False

    def command(self, command):
        fl = open(self.file_path, 'a')
        #fl.writelines(self.separator)
        fl.writelines(command)
        fl.close()


pig = CommandPy(PIG_LATIN_SHELL)
command = []

while True:
    enter_command = raw_input(">>")
    if enter_command == 'quite':
        break
    command.append(enter_command)
    code = pig.returnCode(command)
    if code:
        print code
    else:
        print pig.last_error
    command = []

