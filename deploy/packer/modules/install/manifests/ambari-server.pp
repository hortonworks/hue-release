class install::ambari-server{

  include install::ambari-agent

  package {"ambari-server":
    ensure => installed,
    require => Exec["ambari-repo"]
  }

#  exec {"ambari-server hive patch":
#    command => 'sed -i.bak "s/metatool -listFSRoot 2>\/dev\/null | grep hdfs:\/\//metatool -listFSRoot 2>\/dev\/null | grep hdfs:\/\/ |  grep -v \\\\\".db$\\\\\"/g" /var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/HIVE/package/scripts/hive_service.py',
#    require => [Package["ambari-server"]]
#  }


  exec {"ambari-server setup":
    command => 'ambari-server setup -j `source /etc/profile.d/java.sh; echo $JAVA_HOME` -s',
#    require => [Exec["ambari-server hive patch"]]
  }


  exec { "slider accumulo":
    command => 'wget -N http://public-repo-1.hortonworks.com/HDP/centos6/2.x/updates/2.2.4.2/slider-app-packages/accumulo/slider-accumulo-app-package-1.6.1.2.2.4.2-2.zip && cp slider-accumulo*.zip /var/lib/ambari-server/resources/apps/',
    cwd => "/var/cache/wget",
    logoutput => true,
    require => Exec["ambari-server setup"]
  }

  exec { "slider hbase":
    command => 'wget -N http://public-repo-1.hortonworks.com/HDP/centos6/2.x/updates/2.2.4.2/slider-app-packages/hbase/slider-hbase-app-package-0.98.4.2.2.4.2-2-hadoop2.zip && cp slider-hbase*.zip /var/lib/ambari-server/resources/apps/',
    cwd => "/var/cache/wget",
    logoutput => true,
    require => Exec["ambari-server setup"]
  }

  exec { "slider storm":
    command => 'wget -N http://public-repo-1.hortonworks.com/HDP/centos6/2.x/updates/2.2.4.2/slider-app-packages/storm/slider-storm-app-package-0.9.3.2.2.4.2-2.zip && cp slider-storm*.zip /var/lib/ambari-server/resources/apps/',
    cwd => "/var/cache/wget",
    logoutput => true,
    require => Exec["ambari-server setup"]
  }

  exec {"ambari-server start":
    command => "ambari-server start",
    require => [Exec["ambari-server setup"], Exec["slider accumulo"], Exec["slider hbase"], Exec["slider storm"]]
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
