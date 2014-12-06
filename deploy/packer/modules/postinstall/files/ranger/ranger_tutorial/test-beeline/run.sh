#!/bin/bash
user=hive
if [ $# -gt 0 ]; then
    user=${1}
fi
password=$user

if [ $# -gt 1 ]; then
    password=$2
fi

set -x
#beeline --silent=true -u "jdbc:hive2://sandbox.hortonworks.com:10000/default;auth=noSasl" -n $user -p $password -d org.apache.hive.jdbc.HiveDriver
beeline --silent=true -u "jdbc:hive2://sandbox.hortonworks.com:10000/default" -n $user -p $password -d org.apache.hive.jdbc.HiveDriver
