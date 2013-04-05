#!/bin/bash

set -e

source /usr/lib/hue/tools/start_scripts/consts.sh

PYTHON=/usr/lib/tutorials/.env/bin/python


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
git fetch
git checkout $TUTORIALS_BRANCH
git pull origin $TUTORIALS_BRANCH # >/dev/null 2>&1
echo "Done"
cd $RUN_DIR

# updating tutorials version
if [[ -f 'git_files/version' ]]; then
cat $GIT_FILES/version > /tmp/tutorials_version.info
fi

[ ! -L $RUN_DIR/git_files ] && ln -s $GIT_FILES $RUN_DIR/git_files

echo -n "Updating DB...  "
$PYTHON run.py &>/dev/null
echo "Done"
