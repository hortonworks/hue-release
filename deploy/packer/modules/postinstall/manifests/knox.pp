class postinstall::knox{

  package{"knox*":
    ensure => installed,
    # require => Class["install::ambari-bluprints"]
  }

  exec{"create knox master":
    command => "su -l knox -c '/usr/hdp/current/knox/bin/knoxcli.sh create-master --master knox'",
    require => Package["knox*"]
  }

  
}
