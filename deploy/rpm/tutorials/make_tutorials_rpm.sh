#!/bin/bash

set -e
set -v

source ../env.sh

# === sources ===

[ -f tutorials-env.tgz ] || exit 1; # .env
[ -f tutorials.tgz ] || exit 1; # tutorials without virtualenv

cp tutorials-env.tgz $BB/rpm/SOURCES/
cp tutorials.tgz $BB/rpm/SOURCES/

cp *.spec $BB/rpm/SPECS/


# === build ===

rpmbuild --define "_topdir $BB/rpm" -ba $BB/rpm/SPECS/hue-tutorials.spec
mv $BB/rpm/RPMS/noarch/*.rpm ./
