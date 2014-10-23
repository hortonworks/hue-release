#!/bin/bash

cd `dirname $0`
echo `pwd`
set -x
for policy in *.json; do
	curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://localhost:6080/service/public/api/policy -d @$policy
done

#Give enough time for the agents to refresh
sleep 30
