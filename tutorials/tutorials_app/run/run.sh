#!/bin/bash

set -e

RUN_DIR=/home/sandbox/tutorials/tutorials_app/run
GIT_REPO=git@github.com:hortonworks/sandbox-tutorials.git

GIT_FILES=/home/sandbox/sandbox-tutorials

PYTHON=/home/sandbox/tutorials/.env/bin/python

if [[ "$1" == "--migrate" ]]; then
    echo "Migrating DB..."
    cd $RUN_DIR
    cd "$RUN_DIR/../db"
    rm -f lessons.db
    cd ../../
    ./.env/bin/python manage.py syncdb
    exit 0
fi


cd $RUN_DIR

[ -d $GIT_FILES ] || mkdir -p $GIT_FILES
cd $GIT_FILES
[ ! -d .git ] && git init && git remote add origin $GIT_REPO
echo -n "Pull...  "
git pull origin master # >/dev/null 2>&1
echo "Done"
cd $RUN_DIR

# updating tutorials version
if [[ -f 'git_files/version' ]]; then
cat $GIT_FILES/version > /tmp/tutorials_version.info
fi

echo -n "Updating DB...  "
$PYTHON run.py &>/dev/null
echo "Done"
