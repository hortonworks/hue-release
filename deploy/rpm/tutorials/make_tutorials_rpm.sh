#!/bin/bash

set -e
set -v

source ../env.sh

# === sources ===

[ -f tutorials-env.tgz ] || exit 1; # .env
[ -f tutorials.tgz ] || exit 1; # tutorials without virtualenv

cp tutorials-env.tgz ~/rpm/SOURCES/
cp tutorials.tgz ~/rpm/SOURCES/

cp *.spec ~/rpm/SPECS/


# === build ===

rpmbuild -ba ~/rpm/SPECS/sandbox-tutorials-files.spec
mv ~/rpm/RPMS/noarch/*.rpm ./
