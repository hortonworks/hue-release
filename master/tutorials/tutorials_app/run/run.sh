#!/bin/bash

RUN_DIR=/home/roma/Projects/hdps/tutorials/tutorials_app/run
GIT_REPO=ssh://git@bitbucket.org/antigluk/lessons.git

cd $RUN_DIR

cd git_files
[ ! -d .git ] && git init && git remote add origin $GIT_REPO
echo -n "Pull...  "
git pull origin master >/dev/null 2>&1
echo "Done"
cd - >/dev/null
echo -n "Updating DB...  "
python run.py >/dev/null
echo "Done"
