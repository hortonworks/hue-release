#!/bin/bash

# script starts synchronously on tty1

LOG="/var/log/startup_script.log"

python /home/sandbox/start_scripts/splash.py

(
 nohup sudo -u sandbox bash /home/sandbox/tutorials/tutorials_app/run/run.sh
)  >> $LOG 2>&1 & 
