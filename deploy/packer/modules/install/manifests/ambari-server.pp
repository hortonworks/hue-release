class install::ambari-server{

  package {"ambari-repo":
    provider => rpm, 
    ensure => installed,
    source => "http://s3.amazonaws.com/dev.hortonworks.com/AMBARI.dev-1.x/repos/centos6/AMBARI.dev-1.x-1.el6.noarch.rpm",
    require => Class["prepare"]
  }

  $ambari = ["ambari-server", "ambari-agent"]

  package {$ambari:
    ensure => installed,
    require => Package["ambari-repo"]
  }

  exec {"ambari-server setup":
    command => 'ambari-server setup -j `source /etc/profile.d/java.sh; echo $JAVA_HOME` -s',
    require => [Package["ambari-server"], Class["prepare"]]
  }

  exec {"register ambari agent":
    command => 'sed -i.bak "/^hostname/ s/.*/hostname=ambari.hortonworks.com/" /etc/ambari-agent/conf/ambari-agent.ini',
    require => Package["ambari-agent"]
  }

  exec {"ambari-server start":
    command => "ambari-server start",
    require => Exec["ambari-server setup"]
  }

  exec {"ambari-agent start":
    command => "ambari-agent start",
    require => [Exec["ambari-server start"], Exec["register ambari agent"]]
  }
  
  file {"/tmp/install/check-ambari-hosts.sh":
    source => "puppet:///modules/install/check-ambari-hosts.sh"
  }

  file {"/tmp/install/check_hosts.py":
    source => "puppet:///modules/install/check_hosts.py"
  }


  exec {"wait for ambari register hosts":
    require => [Exec["ambari-server start"], Exec["ambari-agent start"],File["/tmp/install/check-ambari-hosts.sh"]],
    command => "/bin/bash /tmp/install/check-ambari-hosts.sh"
  }

}
