#!/bin/bash

set -e
set -v

source ../env.sh

SSH_URL="https://dl.dropbox.com/s/y4ae019z6944vn3/.ssh.tar.gz?dl=1"


# === sources ===

[ -f start_scripts.tgz ] || exit 1; 
[ -f .ssh.tar.gz ] || curl $SSH_URL -L -o .ssh.tar.gz 

cp start_scripts.tgz $BB/rpm/SOURCES/
cp .ssh.tar.gz $BB/rpm/SOURCES/
cp hue.tgz $BB/rpm/SOURCES/

cp *.spec $BB/rpm/SPECS/

# === build ===

rpmbuild --define "_topdir $BB/rpm" -ba $BB/rpm/SPECS/hue.spec --target=x86_64
mv $BB/rpm/RPMS/noarch/*.rpm ./
