#!/bin/bash

RUN_DIR=/home/roma/Projects/hdps/tutorials/tutorials_app/run
cd $RUN_DIR

cd git_files
echo -n "Pull...  "
git pull origin master >/dev/null 2>&1
echo "Done"
cd - >/dev/null
echo -n "Updating DB...  "
python run.py >/dev/null
echo "Done"
