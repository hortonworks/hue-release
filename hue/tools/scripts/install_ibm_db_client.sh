#!/bin/sh

ENV_PYTHON=/usr/lib/hue/build/env/bin/python2.6
ENV_EASY_INSTALL="$ENV_PYTHON /usr/lib/hue/build/env/bin/easy_install"
EXT_EGGS_DIR=/usr/lib/hue/desktop/core/ext-eggs
EXT_PY_DIR=/usr/lib/hue/desktop/core/ext-py
EXT_PY_IBM_DB_DIR="$EXT_PY_DIR/ibm-db"

if [ ! -d "$EXT_PY_IBM_DB_DIR" ]; then
  echo "The directory $EXT_PY_IBM_DB_DIR not found. Exiting..."
  exit 1
fi

# DB2 env variables
export IBM_DB_DIR=/home/db2clnt1/sqllib
export IBM_DB_INCLUDE=/home/db2clnt1/sqllib/include
export IBM_DB_LIB=/home/db2clnt1/sqllib/lib64

echo "=====> Building ibm-db egg"
cd $EXT_PY_IBM_DB_DIR
eval "$ENV_PYTHON -c '__import__(\"setuptools.sandbox\").sandbox.run_setup(\"setup.py\", __import__(\"sys\").argv[1:])'" bdist_egg

echo "=====> Copying ibm-db egg to ext eggs directory"
find $EXT_PY_IBM_DB_DIR/dist -type f -name '*.egg' -exec cp {} $EXT_EGGS_DIR \;

echo "=====> Installing ibm-db egg"
/usr/lib/hue/build/env/bin/pip uninstall -y ibm-db
cd $EXT_PY_IBM_DB_DIR && [ ! -e dist ] || eval "$ENV_EASY_INSTALL -Z -N dist/*egg"

echo "=====> Cleaning $EXT_PY_IBM_DB_DIR"
cd $EXT_PY_IBM_DB_DIR && rm -Rf dist build temp *.egg-info
find $EXT_PY_IBM_DB_DIR -name \*.egg-info -o -name \*.py[co] -prune -exec rm -Rf {} \;

echo "=====> Finished"
