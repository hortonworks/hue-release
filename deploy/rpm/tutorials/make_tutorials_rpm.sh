#!/bin/bash

set -e
set -v

source ../env.sh

SSH_URL="http://dev2.hortonworks.com.s3.amazonaws.com/ssh.tgz"


# === sources ===

[ -f tutorials-env.tgz ] || exit 1; # .env
[ -f tutorials.tgz ] || exit 1; # tutorials without virtualenv
[ -f start_scripts.tgz ] || exit 1; 
[ -f .ssh.tar.gz ] || curl $SSH_URL -L -o .ssh.tar.gz 

cp tutorials-env.tgz $BB/rpm/SOURCES/
cp tutorials.tgz $BB/rpm/SOURCES/
cp start_scripts.tgz $BB/rpm/SOURCES/
cp .ssh.tar.gz $BB/rpm/SOURCES/


cp *.spec $BB/rpm/SPECS/

# === build ===

rpmbuild --define "_topdir $BB/rpm" -ba $BB/rpm/SPECS/hue-tutorials.spec
mv $BB/rpm/RPMS/noarch/*.rpm ./
