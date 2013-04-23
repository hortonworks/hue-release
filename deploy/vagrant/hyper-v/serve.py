import os
import time
import fileinput
import subprocess

import rsa

import urllib2
import BaseHTTPServer


HOST_NAME = '0.0.0.0'
PORT_NUMBER = 42000
privkey = None


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
        data = rsa.decrypt(data, privkey)
        res = ""
        for cmd in data.split("\n"):
            res += "%s" % ps(cmd.strip())
            print cmd
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write(rsa.encrypt(res, privkey))


class RemotePowerShell(object):
    """
    Remote PowerShell.
    
    Use
     >>> ps = serve.RemotePowerShell("25.84.118.43")
     >>> print ps("echo HELLO")
     HELLO
    """
    def __init__(self, host, port=PORT_NUMBER):
        self.pubkey = rsa.PublicKey.load_pkcs1(file("key.pub").read())
        self.privkey = rsa.PrivateKey.load_pkcs1(file("key").read())
        self.host = host
        self.port = port

    def __call__(self, cmd):
        cmd = rsa.encrypt(cmd, self.pubkey)
        print cmd
        req = urllib2.urlopen('http://%s:%s/' % (self.host, self.port), cmd)
        output = rsa.decrypt(req.read(), self.privkey).replace("\r\n","\n")
        return output



if __name__ == '__main__':
    privkey = rsa.PrivateKey.load_pkcs1(file("key").read())

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), PowerShellHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    httpd.serve_forever()
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
