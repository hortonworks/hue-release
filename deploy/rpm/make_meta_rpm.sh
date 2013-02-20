#!/bin/bash

set -e
set -v

source env.sh

# === sources ===

cp *.spec ~/rpm/SPECS/

# === build ===

rpmbuild -ba ~/rpm/SPECS/sandbox-meta.spec
mv ~/rpm/RPMS/noarch/*.rpm ./
