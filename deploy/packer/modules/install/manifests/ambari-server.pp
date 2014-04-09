class install::ambari-server{

  package {"ambari-repo":
    provider => rpm, 
    ensure => installed,
    source => "http://s3.amazonaws.com/dev.hortonworks.com/AMBARI.dev-1.x/repos/centos6/AMBARI.dev-1.x-1.el6.noarch.rpm"
  }

  package {"ambari-server":
    ensure => installed,
    require => Package["ambari-repo"]
  }

  package {"ambari-agent":
    ensure => installed,
    require => Package["ambari-repo"]
  }

  exec {"ambari-server setup":
    command => "ambari-server setup -j /usr/java/jdk1.7.0_51 -s",
    require => [Package["ambari-server"], Class["prepare"]]
  }

  exec {"register ambari agent":
    command => "sed -i.bak '/^hostname/ s/.*/hostname=sandbox.hortonworks.com/' /etc/ambari-agent/conf/ambari-agent.ini && sleep 10;",
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

  file {"/tmp/check-ambari-hosts.sh":
    source => "puppet:///modules/install/check-ambari-hosts.sh"
  }

  exec {"wait for ambari register hosts":
    require => [Exec["ambari-server start"], Exec["ambari-agent start"],File["/tmp/check-ambari-hosts.sh"]],
    command => "/bin/bash /tmp/check-ambari-hosts.sh"
  }

}
