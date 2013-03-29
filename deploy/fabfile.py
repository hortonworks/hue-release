from __future__ import with_statement

import os

from fabric.api import env, run, local, cd, sudo
from fabric.operations import get
from fabric.contrib.files import exists, sed

from tinydav import WebDAVClient

env.user = 'root'
env.password = 'hadoop'


def update_rpm(branch):
    if not exists('/home/sandbox/rpm-shared/'):
        sudo('cd /home/sandbox/ && git clone git@github.com:'
             '/hortonworks/sandbox-shared.git rpm-shared', user='sandbox')
    sudo('cd /home/sandbox/rpm-shared/ && git reset --hard HEAD')
    sudo('cd /home/sandbox/rpm-shared/ && git fetch '
         '&& git checkout %s && git pull' % branch, user='sandbox')
    sed('/home/sandbox/rpm-shared/deploy/rpm/build.sh', 'Caterpillar', branch)
    sed('/home/sandbox/rpm-shared/deploy/rpm/build.sh', '# export GIT_SSH', 'export GIT_SSH')


def build_rpm(name='repo'):
    # run('rm -rf /root/rpmbuild/out')
    run('cd /home/sandbox/rpm-shared/deploy/rpm/ && bash build.sh')
    local('rm -rf ./repo')
    get('/root/rpmbuild/out', './' + name)


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
    do_upload(client, './' + name + '/out', location='/dav/HortonWorks/%s' % name)


def rpm(name="repo", branch="Caterpillar"):
    update_rpm(branch)
    build_rpm(name)
    upload(name)
    print "Done!"
    print ("baseurl=https://roman.rader%%40gmail.com:storage_1"
           "@www.box.com/dav/HortonWorks/%s" % name)


def hello(v='1'):
    run('echo hello %s' % v)
