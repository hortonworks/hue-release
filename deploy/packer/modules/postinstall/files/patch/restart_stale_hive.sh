#!/bin/bash
for i in HIVE; do 
	
	#stop required service
	curl --user admin:admin -X POST -H 'X-Requested-By: ambari' -d  "{\"RequestInfo\":{\"command\":\"RESTART\",\"context\":\"Restart all components with Stale Configs for HIVE\",\"operation_level\":{\"level\":\"SERVICE\",\"cluster_name\":\"Sandbox\",\"service_name\":\"HIVE\"}},\"Requests/resource_filters\":[{\"service_name\":\"HIVE\",\"component_name\":\"WEBHCAT_SERVER\",\"hosts\":\"sandbox.hortonworks.com\"}]}" "http://127.0.0.1:8080/api/v1/clusters/Sandbox/requests"

	#wait for service to restart
	until /usr/bin/curl -s --user admin:admin -H "X-Requested-By: ambari" "http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/requests?to=end&page_size=10&fields=Requests" | grep -A3 "Restart all components with Stale Configs for HIVE" | grep COMPLETED; do echo 1; sleep 1; done;

done
