#!/bin/bash
while [ 1 ]
do
    hosts=`curl -i -H 'X-Requested-By: ambari' -u admin:admin '127.0.0.1:8080/api/v1/hosts' |grep sandbox`
    if [[ $? -eq 0 ]]
    then
        exit
    else
        sleep 5
    fi
done
