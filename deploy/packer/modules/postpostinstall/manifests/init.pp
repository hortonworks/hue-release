class postpostinstall{
  exec { "slider_fix":
    command => 'su hdfs -c "hdfs dfs -mkdir /user/yarn"; su hdfs -c "hdfs dfs -chown yarn:hdfs /user/yarn"',
    logoutput => true
  }

/*
  exec {"tez_fix":
    command => 'bash ./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox tez-site "tez.lib.uris" "hdfs:///apps/tez/tez.tar.gz"',
    cwd => "/var/lib/ambari-server/resources/scripts",
    logoutput => true
  }

  exec {"restart tez":
    command => '/usr/bin/curl  -H "X-Requested-By: ambari"  -u admin:admin -d \'{"RequestInfo":{"command":"RESTART","context":"Restart all components with Stale Configs for TEZ (puppet)","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"TEZ"}},"Requests/resource_filters":[{"service_name":"TEZ","component_name":"TEZ_CLIENT","hosts":"sandbox.hortonworks.com"}]}\' http://127.0.0.1:8080/api/v1/clusters/Sandbox/requests | python /tmp/wait_finish.py; sleep 5',
    require => [Exec["tez_fix"], File["wait_finish.py"]]
  }
*/
}
