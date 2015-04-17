class install::ambari-bluprints{

  if $nodecount==3{
    if $stack == 'gluster' {
      exec{"register correct stack":
        command => "curl -f -H 'X-Requested-By: ambari' -u admin:admin  -X PUT -d @/tmp/puppet/modules/install/files/2.1.repo.json 'http://ambari.hortonworks.com:8080/api/v1/stacks/HDP/versions/2.1.GlusterFS/operating_systems/centos6/repositories/HDP-2.1.GlusterFS' && wget -O /etc/yum.repos.d/hdp-util.repo http://public-repo-1.hortonworks.com.s3.amazonaws.com/HDP-UTILS-1.1.0.17/repos/centos6/hdp-util.repo",
        require => Class["install::ambari-server"]
      }      
      file{"/tmp/install/bluprint.json":
        source => "puppet:///modules/install/bluprint-gluster-3-nodes.json",
        require => Exec["register correct stack"]
      }
    }
    else {
      file{"/tmp/install/bluprint.json":
        source => "puppet:///modules/install/bluprint-3-nodes.json"
      }
    }
    file{"/tmp/install/cluster.json":
      source => "puppet:///modules/install/3-nodes-bluprint-cluster.json"
    }    
  } 
  else {
    file{"/tmp/install/bluprint.json":
      source => "puppet:///modules/install/bluprint-1-nodes.json"
    }
    file{"/tmp/install/cluster.json":
      source => "puppet:///modules/install/1-nodes-bluprint-cluster.json"
    }
  }

  file{"/tmp/install/check_status.py":
    source => "puppet:///modules/install/check_status.py" 
  }

  file{"/tmp/install/check_status.sh":
    source => "puppet:///modules/install/check_status.sh" 
  }

  file{"/tmp/install/pin_repo.json":
    content => '{"Repositories":{"base_url":"http://public-repo-1.hortonworks.com/HDP/centos6/2.x/updates/2.2.4.2/","verify_base_url":false}}'
  }

  exec {"pin repo":
    command => "curl -X PUT -f -H 'X-Requested-By: ambari' -u admin:admin http://ambari.hortonworks.com:8080/api/v1/stacks/HDP/versions/2.2/operating_systems/redhat6/repositories/HDP-2.2 -d @/tmp/install/pin_repo.json",
    require => [File["/tmp/install/bluprint.json"],Class["install::ambari-server"]],
    logoutput => true
  }

  exec {"add bluprint":
    command => "curl -f -H 'X-Requested-By: ambari' -u admin:admin http://ambari.hortonworks.com:8080/api/v1/blueprints/sandbox -d @/tmp/install/bluprint.json",
    require => [File["/tmp/install/bluprint.json"],Exec["pin repo"]],
    logoutput => true
  }

  exec {"add cluster":
    command => "curl -f -H 'X-Requested-By: ambari' -u admin:admin http://ambari.hortonworks.com:8080/api/v1/clusters/Sandbox -d @/tmp/install/cluster.json",
    require => [File["/tmp/install/cluster.json"],Exec["add bluprint"]],
    logoutput => true
  }

  exec {"install cluster":
    command => "/bin/bash /tmp/install/check_status.sh",
    cwd => "/tmp/install",
    timeout => 0,
    logoutput => true,
    require => [File["/tmp/install/check_status.py"], File["/tmp/install/check_status.sh"], Exec["add cluster"]],
    returns => [0, 1]
  }

  ambariApi {"start everything again":
    url => "services",
    method => "PUT",
    body => '{"RequestInfo":{"context":"_PARSE_.START.ALL_SERVICES","operation_level":{"level":"CLUSTER","cluster_name":"Sandbox"}},"Body":{"ServiceInfo":{"state":"STARTED"}}}',
  }

  exec{'set_hadoop_path':
    command => "echo 'export PATH=\$PATH:/usr/hdp/current/falcon-client/bin:/usr/hdp/current/hadoop-mapreduce-historyserver/bin:/usr/hdp/current/oozie-client/bin:/usr/hdp/current/falcon-server/bin:/usr/hdp/current/hadoop-yarn-client/bin:/usr/hdp/current/oozie-server/bin:/usr/hdp/current/flume-client/bin:/usr/hdp/current/hadoop-yarn-nodemanager/bin:/usr/hdp/current/pig-client/bin:/usr/hdp/current/flume-server/bin:/usr/hdp/current/hadoop-yarn-resourcemanager/bin:/usr/hdp/current/slider-client/bin:/usr/hdp/current/hadoop-client/bin:/usr/hdp/current/hadoop-yarn-timelineserver/bin:/usr/hdp/current/sqoop-client/bin:/usr/hdp/current/hadoop-hdfs-client/bin:/usr/hdp/current/hbase-client/bin:/usr/hdp/current/sqoop-server/bin:/usr/hdp/current/hadoop-hdfs-datanode/bin:/usr/hdp/current/hbase-master/bin:/usr/hdp/current/storm-client/bin:/usr/hdp/current/hadoop-hdfs-journalnode/bin:/usr/hdp/current/hbase-regionserver/bin:/usr/hdp/current/storm-nimbus/bin:/usr/hdp/current/hadoop-hdfs-namenode/bin:/usr/hdp/current/hive-client/bin:/usr/hdp/current/storm-supervisor/bin:/usr/hdp/current/hadoop-hdfs-nfs3/bin:/usr/hdp/current/hive-metastore/bin:/usr/hdp/current/zookeeper-client/bin:/usr/hdp/current/hadoop-hdfs-portmap/bin:/usr/hdp/current/hive-server2/bin:/usr/hdp/current/zookeeper-server/bin:/usr/hdp/current/hadoop-hdfs-secondarynamenode/bin:/usr/hdp/current/hive-webhcat/bin:/usr/hdp/current/hadoop-mapreduce-client/bin:/usr/hdp/current/knox-server/bin:/usr/hdp/current/hadoop-client/sbin:/usr/hdp/current/hadoop-hdfs-nfs3/sbin:/usr/hdp/current/hadoop-yarn-client/sbin:/usr/hdp/current/hadoop-hdfs-client/sbin:/usr/hdp/current/hadoop-hdfs-portmap/sbin:/usr/hdp/current/hadoop-yarn-nodemanager/sbin:/usr/hdp/current/hadoop-hdfs-datanode/sbin:/usr/hdp/current/hadoop-hdfs-secondarynamenode/sbin:/usr/hdp/current/hadoop-yarn-resourcemanager/sbin:/usr/hdp/current/hadoop-hdfs-journalnode/sbin:/usr/hdp/current/hadoop-mapreduce-client/sbin:/usr/hdp/current/hadoop-yarn-timelineserver/sbin:/usr/hdp/current/hadoop-hdfs-namenode/sbin:/usr/hdp/current/hadoop-mapreduce-historyserver/sbin:/usr/hdp/current/hive-webhcat/sbin' > /etc/profile.d/hadoop.sh;",
    require => Exec["install cluster"]
  }

  exec{'hadoop_path_add':    
    command => 'sed -i.bak "s/exec /source \/etc\/profile.d\/hadoop.sh\nexec /g" /usr/hdp/current/hadoop-client/bin/hadoop',
    require => Exec["install cluster"]
  }

}

