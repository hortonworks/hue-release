from subprocess import Popen, PIPE

class Command:

    file_path = ''
    shell_path = ''
    last_error = ''

    #def __init__(self, shell_path=""):
        #self.shell_path = shell_path.split()
        #self.file_path = self.shell_path[-1]

    def executeOld(self, what=''):
        if what:
            self.commandOld(what)
        p = Popen(self.shell_path, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        answer, error = p.communicate()
        if not answer:
            self.last_error = error
            return False
        else:
            return answer

    def commandOld(self, command):
        fl = open(self.file_path, 'a')
        fl.writelines(command)
        fl.close()
            
    def execute(self, what):
        if not what:
            self.last_error = ""
            return False
        #p = Popen("hcat -e " + what, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        #answer, error = p.communicate()
        p = Popen(["ssh -t centos@192.168.56.101"], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        #answer, error = p.communicate(input="ls")
        answer, error = p.communicate(input="hcat -e '" + what + "'")
        if not answer:
            self.last_error = error
            return False
        else:
            return answer
        
    def executeFromFile(self, what):
        if not what:
            self.last_error = ""
            return False
        p = Popen("hcat -f " + what, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        answer, error = p.communicate()
        if not answer:
            self.last_error = error
            return False
        else:
            return answer


