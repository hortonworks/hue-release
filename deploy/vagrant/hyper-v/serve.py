import os
import time
import fileinput
import subprocess

from SimpleAES import SimpleAES
import base64

import urllib2
import BaseHTTPServer


HOST_NAME = '0.0.0.0'
PORT_NUMBER = 42000
aes = None


def ps(cmd):
    fcmd = r'"C:\WINDOWS\system32\WindowsPowerShell\v1.0\powershell.exe" '\
                          '-ExecutionPolicy '\
                          'Unrestricted ' + cmd
    ps = subprocess.Popen(fcmd, cwd=os.getcwd(), stdout=subprocess.PIPE,
                          shell=True)
    return ps.communicate()[0]


class PowerShellHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(s):
        length = int(s.headers.getheader("content-length"))
        data = s.rfile.read(length)
        data = base64.b64decode(aes.decrypt(data))
        res = ""
        for cmd in data.split("\n"):
            res += "%s" % ps(cmd.strip())
            print cmd
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        res = base64.b64encode(res)
        s.wfile.write(aes.encrypt(res))


class RemotePowerShell(object):
    """
    Remote PowerShell.
    
    Use
     >>> ps = serve.RemotePowerShell("25.84.118.43")
     >>> print ps("echo HELLO")
     HELLO
    """
    def __init__(self, host, port=PORT_NUMBER, key=None):
        self.host = host
        self.port = port
        if key:
            self.aes = SimpleAES(file(key).read())
        else:
            self.aes = SimpleAES(file("key").read())

    def __call__(self, cmd, oneline=True):
        if oneline:
            cmd = cmd.replace('\n', '; ')
        cmd = self.aes.encrypt(base64.b64encode(cmd))
        req = urllib2.urlopen('http://%s:%s/' % (self.host, self.port), cmd)
        output = self.aes.decrypt(req.read())
        output = base64.b64decode(output)
        output = output.replace("\r\n","\n")
        return output



if __name__ == '__main__':
    aes = SimpleAES(file("key").read())
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), PowerShellHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    httpd.serve_forever()
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
