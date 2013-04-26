#!/usr/bin/python2

import sys
import serve
import getopt

def main(argv):                          
    grammar = "kant.xml"                
    try:                                
        opts, args = getopt.getopt(argv[1:], "s:h:p:k:", [])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    script = None
    host = None
    key = None
    port = 42000
    for opt, arg in opts:
        if opt in ("-s", ):
            script = arg
            if script == '--':
                script = sys.stdin.read()
        if opt in ("-h", ):
            host = arg
        if opt in ("-p", ):
            port = arg
        if opt in ("-k", ):
            key = arg
    
    if not (script and host):
        usage()
        sys.exit(2)

    ps = serve.RemotePowerShell(host, port, key)
    print ps(script)


def usage():
    print "%s -s 'command' -h example.com [-p 42000]" % (sys.argv[0])


if __name__ == '__main__':
    main(sys.argv)