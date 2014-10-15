class install::ambari-server{

  include install::ambari-agent

  package {"ambari-server":
    ensure => installed,
    require => Exec["ambari-repo"]
  }

  exec {"ambari-server hive patch":
    command => 'sed -i.bak "s/metatool -listFSRoot 2>\/dev\/null | grep hdfs:\/\//metatool -listFSRoot 2>\/dev\/null | grep hdfs:\/\/ |  grep -v \\\\\".db$\\\\\"/g" /var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/HIVE/package/scripts/hive_service.py',
    require => [Package["ambari-server"]]
  }


  exec {"ambari-server setup":
    command => 'ambari-server setup -j `source /etc/profile.d/java.sh; echo $JAVA_HOME` -s',
    require => [Exec["ambari-server hive patch"]]
  }


  exec {"ambari-server start":
    command => "ambari-server start",
    require => [Exec["ambari-server setup"]]
  }

  file {"/tmp/install/check-ambari-hosts.sh":
    source => "puppet:///modules/install/check-ambari-hosts.sh"
  }

  file {"/tmp/install/check_hosts.py":
    source => "puppet:///modules/install/check_hosts.py"
  }

  exec {"wait for ambari register hosts":
    require => [Exec["ambari-server start"], Class["install::ambari-agent"],File["/tmp/install/check-ambari-hosts.sh"],File["/tmp/install/check_hosts.py"]],
    command => "/bin/bash /tmp/install/check-ambari-hosts.sh",
    timeout => 1000
  }

}
