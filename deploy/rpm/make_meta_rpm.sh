#!/bin/bash

set -e
set -v

source env.sh

# === sources ===

cp *.spec $BB/rpm/SPECS/

# === build ===

rpmbuild --define "_topdir $BB/rpm" -ba $BB/rpm/SPECS/sandbox-meta.spec
mv $BB/rpm/RPMS/noarch/*.rpm ./
