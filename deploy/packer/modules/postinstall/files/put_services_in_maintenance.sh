#!/bin/bash
for i in SPARK HBASE FALCON STORM KAFKA FLUME AMBARI_METRICS; do 
	
	#stop required service
	curl --user admin:admin -X PUT -H "X-Requested-By: ambari"  -d "{\"RequestInfo\":{\"context\":\"Stop required services\",\"operation_level\":{\"level\":\"SERVICE\",\"cluster_name\":\"Sandbox\",\"service_name\":\"$i\"}},\"Body\":{\"ServiceInfo\":{\"state\":\"INSTALLED\"}}}" "http://localhost:8080/api/v1/clusters/Sandbox/services/$i"

	#wait for service to stop
	until /usr/bin/curl -s --user admin:admin -H "X-Requested-By: ambari" "http://localhost:8080/api/v1/clusters/Sandbox/services/$i" | grep INSTALLED; do echo 1; sleep 1; done;

	#send the maintenance command
	curl -u admin:admin -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo":{"context":"Turn Off Maintenance Mode"},"Body":{"ServiceInfo":{"maintenance_state":"ON"}}}' "http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/$i"

	#wait for the service to go into maintenance mode
	until /usr/bin/curl -s --user admin:admin -H "X-Requested-By: ambari" "http://localhost:8080/api/v1/clusters/Sandbox/services/$i" | grep -i maintenance | grep -i on; do echo 1; sleep 1; done;
done
