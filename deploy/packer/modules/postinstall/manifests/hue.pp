class postinstall::hue{

  package{"hue":
    ensure => installed,
    # require => Class["install::ambari-bluprints"]
  }

  exec { "hue_fix":
    command => "sed -i.bak 's/import urllib/import urllib,os,json/' /usr/lib/hue/desktop/core/src/desktop/auth/views.py",
    logoutput => true
  }

  file { "/etc/hue/conf/hue.ini":
    source => "puppet:///modules/postinstall/hue.ini",
    require => Package['hue']
  }

  service{"hue":
    ensure => running,
    require => [File["/etc/hue/conf/hue.ini"],Package["hue"], Exec["hue_fix"]]
  }


  file { "/tmp/install/hdfs_prepare.sh":
    source => "puppet:///modules/postinstall/hdfs_prepare.sh"
  }

  exec {"prepare_hue":
    command => "/bin/bash /tmp/install/hdfs_prepare.sh",
    require => [File["/tmp/install/hdfs_prepare.sh"],Service["hue"]],
    timeout => 0
  }

  exec{"ranger_create_hue_users":
    cwd => "/tmp/ranger_tutorial/hue",
    command => "/bin/bash /tmp/ranger_tutorial/hue/setup_data.sh",
    require => Exec["prepare_hue"],
    logoutput => true,
  }

}
