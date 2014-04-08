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
    command => "sed -i.bak '/^hostname/ s/.*/hostname=sandbox.hortonworks.com/' /etc/ambari-agent/conf/ambari-agent.ini",
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
  
  exec {"wait for ambari-server":
    require => Exec["ambari-server start"],
    command => "/usr/bin/wget --spider --tries 20 --retry-connrefused --no-check-certificate http://127.0.0.1:8080",
  }
    
}
