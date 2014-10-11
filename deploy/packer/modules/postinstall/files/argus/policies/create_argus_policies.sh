#!/bin/bash

cd `dirname $0`
#Create HDFS repository
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/repository -d @/tmp/repo_hdfs.json

#Add HDFS Policies
curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/policy -d @/tmp/policies_hdfs_public.json

