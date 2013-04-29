from __future__ import with_statement

import os
import json

from fabric.api import env, run, local
from fabric.operations import get
from fabric.contrib.files import exists, sed

import boto
import boto.s3.key


env.user = 'sandbox'
env.password = '1111'


# load credentials from a predefined file
CREDENTIALS = json.load(open('./aws_credentials.json'))
AWS_ACCESS_KEY_ID = CREDENTIALS['access_key']
AWS_SECRET_ACCESS_KEY = CREDENTIALS['secret_key']
BUCKET_NAME = CREDENTIALS['bucket']


def update_rpm(branch):
    "update git on server and checkout selected branch. args: branch"
    if not exists('/home/sandbox/rpm-shared/'):
        run('cd /home/sandbox/ && git clone git@github.com:'
            '/hortonworks/sandbox-shared.git rpm-shared')
    run('cd /home/sandbox/rpm-shared/ && git reset --hard HEAD^^')
    run('cd /home/sandbox/rpm-shared/ && git fetch '
        '&& git checkout %s && git pull' % branch)
    sed('/home/sandbox/rpm-shared/deploy/rpm/build.sh', 'Caterpillar', branch)


def build_rpm():
    "start building rpms. no args"
    run('rm -rf /home/sandbox/rpmbuild/out')
    run('cd /home/sandbox/rpm-shared/deploy/rpm/ && bash build.sh')


def get_out(name='repo'):
    "download rpmbuild result folder, args: dirname"
    local('rm -rf ./' + name)
    get('/home/sandbox/rpmbuild/out', './' + name)


def do_upload(client, path, location='repo/', remote=''):
    if os.path.isfile(path):
        print "put %s to %s" % (path, location + remote)
        k = boto.s3.key.Key(client)
        k.key = location + remote
        k.set_contents_from_filename(path)
        k.make_public()
        return

    files_in_dir = os.listdir(path)
    for f in files_in_dir:
        print f
        do_upload(client, "%s/%s" % (path, f), location=location, remote="%s/%s" % (remote, f))


def upload(name='repo'):
    "upload to s3 rpms. args: s3dir"
    conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                           AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(BUCKET_NAME)

    do_upload(bucket, "%s/out" % name, '%s' % name)


def rpm(name="repo", branch="Caterpillar"):
    "build and upload to s3 rpms. args: s3dir,branch"
    update_rpm(branch)
    build_rpm()
    get_out(name)
    upload(name)
    print "Done!"
    print ("baseurl=https://roman.rader%%40gmail.com:storage_1"
           "@www.box.com/dav/HortonWorks/%s" % name)


def vagrant():
    local("cd ./vagrant; vagrant destroy -f; vagrant up")
