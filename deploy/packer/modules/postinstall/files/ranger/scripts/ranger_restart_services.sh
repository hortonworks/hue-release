#!/bin/bash

cd `dirname $0`
scripts_folder=`pwd`

if [ -f /etc/profile.d/java.sh ]; then
	. /etc/profile.d/java.sh
fi

echo "Restarting services..."

set -x

#Restart all the servers
#NameNode
$scripts_folder/restart_namenode.sh

#HiveServer2
$scripts_folder/restart_hiveservers.sh

#HBase
$scripts_folder/restart_hbase.sh

#Copy the tutorial files to the home folder of root
cd $scripts_folder
cp -r ../ranger_tutorial /root

