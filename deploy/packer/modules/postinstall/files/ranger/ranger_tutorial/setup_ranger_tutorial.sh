#!/bin/bash
#This script will call all dependent scripts to create the users, groups, data and tables
set -x

cd `dirname $0`

rm -rf /tmp/ranger_tutorial
mkdir -p /tmp/ranger_tutorial
cp -r * /tmp/ranger_tutorial
chmod -R 777 /tmp/ranger_tutorial

script_dir=/tmp/ranger_tutorial

#Create the groups, users and hdfs data
cd $script_dir
cd test-hdfs
`pwd`/setup_groups.sh
`pwd`/setup_users.sh

sleep_secs=30
echo "Sleeping for $sleep_secs seconds to let user and group sync to policy mgr"
sleep $sleep_secs

#Give appropriate permission to users to populate the data
cd $script_dir
cd policies
./set_tutorial_policies.sh
./set_audit_policies.sh http://localhost:6080 sandbox_hdfs admin admin


#Setup HDFS
cd $script_dir
cd test-hdfs
runuser -l hdfs -c "`pwd`/setup_data.sh"

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
#cp /etc/knox/conf/topologies/sandbox.xml /etc/knox/conf/topologies/sandbox.xml.$(date +%m%d%y%H%M).by_ranger
cp knox/knox_sample.xml  /etc/knox/conf/topologies
cd /usr/hdp/current/knox-server
sudo -u knox bin/ldap.sh start
	
su -l knox /usr/hdp/current/knox-server/bin/gateway.sh stop
su -l knox /usr/hdp/current/knox-server/bin/gateway.sh start

