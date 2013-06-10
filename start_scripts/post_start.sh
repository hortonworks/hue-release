#!/bin/bash

# script starts synchronously on tty1

LOG="/var/log/startup_script.log"

(
 nohup sudo -u hue bash /usr/lib/tutorials/tutorials_app/run/run.sh
 su - hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf start master"; sleep 5
 su - hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf start regionserver"
)  >> $LOG 2>&1 & 

python /usr/lib/hue/tools/start_scripts/splash.py
