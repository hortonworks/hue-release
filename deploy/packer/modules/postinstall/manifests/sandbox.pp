class postinstall::sandbox{

  yumrepo{"sandbox":
    baseurl => "http://dev2.hortonworks.com.s3.amazonaws.com/repo/dev/baikal-GA-2.3.1/utils/",
    descr => "Sandbox repository (tutorials)",
    enabled => 1,
    gpgcheck => 0,
    require => Class["postinstall"]
  }

  exec{"correct /etc/issue":
    command => "printf 'To login to the the shell, use:\nusername: root\npassword: hadoop' >> /etc/issue"
  }

  exec { 'issue-credentials':
    command => "initctl restart tty TTY=/dev/tty5; initctl restart tty TTY=/dev/tty2; true",
    require => Exec["correct /etc/issue"],
  }

  $hueSandbox = ["hue", "hue-sandbox", "hue-tutorials"]

  package{$hueSandbox:
    ensure => installed,
    require => Yumrepo["sandbox"]
  }

  exec { 'hue_password':
    command => "echo 'hue:hadoop' | chpasswd",
    require => Package['hue']
  }

  exec { 'hue_sudoers':
    command => "echo -e 'hue ALL=(ALL) ALL\nhue ALL=(ALL) NOPASSWD: /sbin/chkconfig\nhue ALL=(ALL) NOPASSWD: /sbin/service\nhue ALL=(ALL) NOPASSWD: /bin/kill' >> /etc/sudoers",
    require => Package['hue']
  }

  file { "/etc/hue/conf/hue.ini":
    source => "puppet:///modules/postinstall/hue.ini",
    require => Package['hue']
  }

  file { "/tmp/install/ambari-url-fix.sh":
    source => "puppet:///modules/postinstall/ambari-url-fix.sh"
  }

  file { "/tmp/install/hdfs_prepare.sh":
    source => "puppet:///modules/postinstall/hdfs_prepare.sh"
  }

  service{"hue":
    ensure => running,
    require => [File["/etc/hue/conf/hue.ini"],Package["hue"]]
  }

  exec {"prepare_hue":
    command => "/bin/bash /tmp/install/hdfs_prepare.sh",
    require => [File["/tmp/install/hdfs_prepare.sh"],Service["hue"]],
    timeout => 0
  }

  exec {'ambari-url-fix.sh':
    command => '/bin/bash /tmp/install/ambari-url-fix.sh',
    require => [File["/tmp/install/ambari-url-fix.sh"], Class["install::ambari-server"]]
  }

  file { '/etc/httpd/conf.d/hue.conf':
    source => "puppet:///modules/postinstall/apache-hue.conf",
    ensure  => file,
    require => Package["hue"]
  }

  include postinstall::splash
}
