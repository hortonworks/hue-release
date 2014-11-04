class postpostinstall{
  exec {"prepare_hue":
    command => "/bin/bash /tmp/install/hdfs_prepare.sh",
    require => [File["/tmp/install/hdfs_prepare.sh"],Service["hue"]],
    timeout => 0
  }

  exec { "slider_fix":
    command => 'su hdfs -c "hdfs dfs -mkdir /user/yarn"; su hdfs -c "hdfs dfs -chown yarn:hdfs /user/yarn"',
    logoutput => true
  }

  exec {"tez_fix":
    command => 'su hdfs -c "hdfs dfs -mkdir /apps/tez"; su hdfs -c "hdfs dfs -put /usr/hdp/current/tez-client/lib/tez*.tar.gz /apps/tez/"; su hdfs -c "hdfs dfs -chown -R hcat:hdfs /apps/tez"; ',
    logoutput => true
  }

  exec {"pig_fix":
    command => 'su hdfs -c "hdfs dfs -mkdir /apps/webhcat"; su hdfs -c "hdfs dfs -put /usr/hdp/current/pig-client/pig*.tar.gz /apps/webhcat/pig.tar.gz"; su hdfs -c "hdfs dfs -chown -R hcat:hdfs /apps/webhcat"; ',
    logoutput => true
  }

  exec {"hive_hcatalog_fix":
    command => 'ln -s /usr/hdp/2.*/hive-hcatalog/ /usr/hdp/current/hive-hcatalog',
    logoutput => true
  }

  ambariApi {"restart hive":
    url => "requests",
    method => "POST",
    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HIVE","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HIVE"}},"Requests/resource_filters":[{"service_name":"HIVE","component_name":"HCAT","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"HIVE_CLIENT","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"HIVE_METASTORE","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"HIVE_SERVER","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"MYSQL_SERVER","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"WEBHCAT_SERVER","hosts":"sandbox.hortonworks.com"}]}'
  }

  ambariApi {"restart hbase":
    url => "requests",
    method => "POST",
    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HBASE","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HBASE"}},"Requests/resource_filters":[{"service_name":"HBASE","component_name":"HBASE_CLIENT","hosts":"sandbox.hortonworks.com"},{"service_name":"HBASE","component_name":"HBASE_MASTER","hosts":"sandbox.hortonworks.com"},{"service_name":"HBASE","component_name":"HBASE_REGIONSERVER","hosts":"sandbox.hortonworks.com"}]}'
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
