from __future__ import with_statement

import os

from fabric.api import env, run, local, sudo
from fabric.operations import get
from fabric.contrib.files import exists, sed

from tinydav import WebDAVClient

env.user = 'sandbox'
env.password = '1111'


def update_rpm(branch):
    if not exists('/home/sandbox/rpm-shared/'):
        run('cd /home/sandbox/ && git clone git@github.com:'
            '/hortonworks/sandbox-shared.git rpm-shared')
    run('cd /home/sandbox/rpm-shared/ && git reset --hard HEAD^^')
    run('cd /home/sandbox/rpm-shared/ && git fetch '
        '&& git checkout %s && git pull' % branch)
    sed('/home/sandbox/rpm-shared/deploy/rpm/build.sh', 'Caterpillar', branch)
    #sed('/home/sandbox/rpm-shared/deploy/rpm/build.sh', '# export GIT_SSH', 'export GIT_SSH')


def build_rpm(name='repo'):
    run('rm -rf /home/sandbox/rpmbuild/out')
    run('cd /home/sandbox/rpm-shared/deploy/rpm/ && bash build.sh')


def get_out(name='repo'):
    local('rm -rf ./' + name)
    get('/home/sandbox/rpmbuild/out', './' + name)


def do_upload(client, path, location='/dav/HortonWorks/repo', remote=''):
    if os.path.isfile(path):
        print "put %s to %s" % (path, location + remote)
        with open(path) as fd:
            client.put(location + remote, fd)
        return

    files_in_dir = os.listdir(path)
    for f in files_in_dir:
        print f
        do_upload(client, "%s/%s" % (path, f), location=location, remote="%s/%s" % (remote, f))


def upload(name='repo'):
    client = WebDAVClient("www.box.com", 443)
    client.setbasicauth("roman.rader@gmail.com", "storage_1")
    try:
        client.mkcol('/dav/HortonWorks/%s' % name)
        client.mkcol('/dav/HortonWorks/%s/repodata' % name)
    except:
        pass
    do_upload(client, './' + name + '/out', location='/dav/HortonWorks/%s' % name)


def rpm(name="repo", branch="Caterpillar"):
    update_rpm(branch)
    build_rpm(name)
    get_out(name)
    upload(name)
    print "Done!"
    print ("baseurl=https://roman.rader%%40gmail.com:storage_1"
           "@www.box.com/dav/HortonWorks/%s" % name)


def vagrant():
    local("cd ./vagrant; vagrant destroy -f; vagrant up")
