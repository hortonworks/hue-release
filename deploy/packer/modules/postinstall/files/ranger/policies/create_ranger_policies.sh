#!/bin/bash

#Make sure this script is run from the folder which contains the policies
#e.g. cd /tmp/ranger/policies
policies_folder=`pwd`

echo "Policies folder=$policies_folder"

set -x
cp * /tmp

#Create HDFS repository
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/repository -d @/tmp/repo_hdfs.json

#Add HDFS Policies
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/policy -d @/tmp/policies_hdfs_public.json

#Create Hive repository
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/repository -d @/tmp/repo_hive.json

#Add Hive Policies
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/policy -d @/tmp/policy_hive_tables_public.json
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/policy -d @/tmp/policy_hive_udf_public.json


#Create HBase repository
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/repository -d @/tmp/repo_hbase.json

#Add HBase Policies
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/policy -d @/tmp/policy_hbase_public.json

#Create Knox repository
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/repository -d @/tmp/repo_knox.json

#Add Knox Policies
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/policy -d @/tmp/policy_knox_public.json

#Create Storm repository
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/repository -d @/tmp/repo_storm.json

#Add Storm Policies
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/policy -d @/tmp/policy_storm_public.json


#Setup Ranger tutorial
cd $policies_folder
cd ../ranger_tutorial
./setup_ranger_tutorial.sh
