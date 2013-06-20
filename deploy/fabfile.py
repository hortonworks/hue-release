from __future__ import with_statement

import os
import json

from fabric.api import env, run, local
from fabric.operations import get, put, sudo
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
    sed('/home/sandbox/rpm-shared/deploy/rpm/build.sh', 'sudo yum -y', '# sudo yum -y')


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


def upload(name='repo', subfolder="/out", local=None):
    "upload to s3 rpms. args: s3dir"
    conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                           AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(BUCKET_NAME)

    if not local:
        local = name
    do_upload(bucket, "%s%s" % (local, subfolder), '%s' % name)


def rpm(name="repo", branch="Caterpillar", bigtop=True):
    "build and upload to s3 rpms. args: s3dir,branch"
    update_rpm(branch)
    build_rpm()
    # if bigtop:
        # run("rm -rf /home/sandbox/rpmbuild/out/repodata")
        # put('./' + name + '-bigtop/hue/*.rpm', '/home/sandbox/rpmbuild/out/')
    run("cd /home/sandbox/rpmbuild/out; createrepo .")
    get_out(name)
    upload(name)
    print "Done!"


def vagrant():
    local("cd ./vagrant; vagrant destroy -f; vagrant up")

build_support = "/home/jenkins/workspace/build-support/"
output_directory = build_support + '%s/output/hue'


def bt_get_out(name='repo', btbranch="bigtop-0.3"):
    "download rpmbuild result folder from BigTop, args: dirname"
    env.host_string = "root@127.0.0.1:2222"
    local('rm -rf ./' + name + '-bigtop')
    get(output_directory % btbranch, './' + name + "-bigtop")
    local('rm -f ./' + name + '-bigtop/hue-*.src.rpm')


def btrpm(name="repo", branch="Caterpillar", btbranch="bigtop-0.3"):
    "build and upload to s3 rpms _using BigTop_. args: s3dir,branch"
    env.host_string = "root@127.0.0.1:2222"

    put("HDP_variables.sh",
        "/home/jenkins/workspace/build-support/HDP_variables.sh")
    sed(build_support + 'HDP_variables.sh', 'Caterpillar', branch)
    sed(build_support + 'HDP_variables.sh', 'bigtop-0.3', btbranch)
    sudo("cd " + build_support + "; BUILD_NUMBER=100 sh bigtop_build.sh hue", user="jenkins")
    sudo("cd " + output_directory % btbranch + "; createrepo .", user="jenkins")
    bt_get_out(name, btbranch)
    upload('bigtop/' + name, "", local=name + '-bigtop/hue')
    print "Done!"
