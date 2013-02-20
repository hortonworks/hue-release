#!/bin/bash

set -e
set -v

source ../env.sh

SSH_URL="https://dl.dropbox.com/s/y4ae019z6944vn3/.ssh.tar.gz?dl=1"
HUE_URL="https://www.dropbox.com/s/p4n9pf37v1bidnd/hue.tar.gz?dl=1"


# === sources ===

[ -f start_scripts.tgz ] || exit 1; 
[ -f .ssh.tar.gz ] || curl $SSH_URL -o .ssh.tar.gz 
[ -f hue.tgz ] || curl $HUE_URL -o hue.tgz

cp start_scripts.tgz ~/rpm/SOURCES/
cp .ssh.tar.gz ~/rpm/SOURCES/
cp hue.tgz ~/rpm/SOURCES/

cp *.spec ~/rpm/SPECS/

# === build ===

rpmbuild -ba ~/rpm/SPECS/sandbox-bin.spec --target=x86_64
mv ~/rpm/RPMS/noarch/*.rpm ./
