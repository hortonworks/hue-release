#!/bin/bash
#This script will call all dependent scripts to create the users, groups, data and tables

cd `dirname $0`

rm -rf /tmp/argus_tutorial
mkdir -p /tmp/argus_tutorial
cp -r * /tmp/argus_tutorial
chmod -R 777 /tmp/argus_tutorial

script_dir=/tmp/argus_tutorial

#Create the groups, users and hdfs data
cd $script_dir
cd test-hdfs
`pwd`/setup_groups.sh
`pwd`/setup_users.sh

sleep_secs=30
echo "Sleeping for $sleep_secs seconds to let user and group sync to policy mgr"
sleep $sleep_secs

#Create Hue users
cd $script_dir
cd hue
`pwd`/setup_data.sh

#Give appropriate permission to users to populate the data
cd $script_dir
cd policies
./set_tutorial_policies.sh


#Setup HDFS
runuser -l hdfs -c "cd `pwd`;`pwd`/setup_data.sh"

#Setup Hive table
cd $script_dir
cd test-beeline
runuser -l hive -c `pwd`/setup_data.sh

#Setup HBase table
cd $script_dir
cd test-hbase
runuser -l hbase -c `pwd`/setup_data.sh

#Enable Knox
cd $script_dir
cp /etc/knox/conf/topologies/sandbox.xml /etc/knox/conf/topologies/sandbox.xml.$(date +%m%d%y%H%M)
cp knox/sandbox.xml  /etc/knox/conf/topologies
cd /usr/hdp/current/knox-server
sudo -u knox bin/ldap.sh
	
su -l knox /usr/hdp/current/knox-server/bin/gateway.sh stop
su -l knox /usr/hdp/current/knox-server/bin/gateway.sh start

