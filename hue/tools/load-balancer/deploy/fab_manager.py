from __future__ import with_statement

import os

from fabric.api import env, run, local
from fabric.operations import get, put, sudo
from fabric.contrib.files import exists, sed

HOST_PWD_PATH = os.getcwd()
HOST_PUPPET_PATH = HOST_PWD_PATH + '/puppet'
HOST_MODULES_PATH = HOST_PUPPET_PATH + '/modules'

TARGET_ROOT = '/tmp'
TARGET_PUPPET_PATH = TARGET_ROOT + '/puppet'
TARGET_MODULES_PATH = TARGET_PUPPET_PATH + '/modules'
TARGET_REVERSE_PROXY_MANIFEST = TARGET_MODULES_PATH + '/load-balancer/manifests/reverse_proxy.pp'


# using:
#     fab -H user@targethost --port=22 -f ./fab_manager.py setup_reverse_proxy


def setup_reverse_proxy():
    put(HOST_PUPPET_PATH, TARGET_ROOT)
    sudo('yum install puppet')
    sudo('puppet apply --modulepath=%s %s' % (TARGET_MODULES_PATH, TARGET_REVERSE_PROXY_MANIFEST))
    sudo('rm -Rf %s' % TARGET_PUPPET_PATH)
