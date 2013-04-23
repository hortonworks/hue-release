import time
import BaseHTTPServer
import subprocess
import os
import fileinput

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 42000


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
        res = ""
        for cmd in s.rfile.read(length).split("\n"):
            res += "%s" % ps(cmd.strip())
            print cmd
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write(res)


class RemotePowerShell(object):
    def __init__(self, host, port=PORT_NUMBER):
        


if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), PowerShellHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    httpd.serve_forever()
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
