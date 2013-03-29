from __future__ import with_statement

import os

from fabric.api import env, run, local, cd, sudo
from fabric.operations import get
from fabric.contrib.files import exists

from tinydav import WebDAVClient

env.user = 'root'
env.password = 'hadoop'


def update_rpm(branch):
    sudo('cd /home/sandbox/rpm-shared/ && git fetch '
        '&& git checkout {} && git pull'.format(branch), user='sandbox')


def build_rpm():
    run('rm -rf /root/rpmbuild/out')
    run('cd /home/sandbox/rpm-shared/deploy/rpm/ && bash build.sh')
    local('rm -rf ./repo')
    get('/root/rpmbuild/out', './repo')


def do_upload(client, path, location='/dav/HortonWorks/repo', remote=''):
    if os.path.isfile(path):
        print "put %s to %s" % (path, remote)
        with open(path) as fd:
            client.put(location + remote, fd)
        return

    files_in_dir = os.listdir(path)
    for f in files_in_dir:
        print f
        do_upload(client, "%s/%s" % (path, f), "%s/%s" % (remote, f))


def upload(name):
    client = WebDAVClient("www.box.com", 443)
    client.setbasicauth("roman.rader@gmail.com", "storage_1")
    do_upload(client, './repo/out', location='/dav/HortonWorks/%s' % name)


def rpm(name="repo", branch="Caterpillar"):
    update_rpm(branch)
    build_rpm()
    upload(name)
    print "Done!"
    print ("baseurl=https://roman.rader%%40gmail.com:storage_1"
           "@www.box.com/dav/HortonWorks/%s" % name)


def hello(v='1'):
    run('echo hello {}'.format(v))
