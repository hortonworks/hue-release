#!/bin/bash
if [ $# -lt 2 ]; then
    echo "Usage: $0 <user> <password>"
    exit 1
fi
user=${1}
password=$2

set -x
#beeline --silent=true -u "jdbc:hive2://sandbox.hortonworks.com:10000/default;auth=noSasl" -n $user -p $password -d org.apache.hive.jdbc.HiveDriver
beeline --silent=true -u "jdbc:hive2://sandbox.hortonworks.com:10000/default" -n $user -p $password -d org.apache.hive.jdbc.HiveDriver
