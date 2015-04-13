class postinstall::knox{

  package{"knox_*":
    ensure => installed,
    # require => Class["install::ambari-bluprints"]
  }

  exec{"create knox master":
    command => "su -l knox -c '/usr/hdp/current/knox-server/bin/knoxcli.sh create-master --master knox'",
    require => Package["knox_*"]
  }

  file { "/etc/knox/sandbox.xml.provided":
    source => "puppet:///modules/postinstall/knox/sandbox.xml",
    require => [Package["knox_*"], Exec["create knox master"]]
  }

  file { "/etc/knox/conf/topologies/sandbox.xml":
    source => "puppet:///modules/postinstall/knox/sandbox.xml",
    require => [Package["knox_*"], Exec["create knox master"], File["/etc/knox/sandbox.xml.provided"]]
  }
  
}
