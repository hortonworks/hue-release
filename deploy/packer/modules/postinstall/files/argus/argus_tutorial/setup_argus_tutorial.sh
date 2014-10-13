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
