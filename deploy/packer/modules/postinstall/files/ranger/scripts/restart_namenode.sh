#/bin/bash

set -x
SCRIPTS_PATH="/usr/lib/hue/tools/start_scripts"

echo "Stop NameNode"
su -l hdfs -c "/usr/hdp/current/hadoop-client/sbin/hadoop-daemon.sh --config /etc/hadoop/conf stop namenode"

sleep 30

#Starting NameNode
make --makefile $SCRIPTS_PATH/start_deps.mf -B namenode -j -i

sleep 60