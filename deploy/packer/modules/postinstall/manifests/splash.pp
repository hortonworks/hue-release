class postinstall::splash {

  file { 'ttys':
    path    => "/tmp/install/start-ttys.override",
    source => "puppet:///modules/postinstall/tty/start-ttys.override"
  }

  file { 'tty1':
    path    => "/tmp/install/tty-splash.conf",
    source => "puppet:///modules/postinstall/tty/tty-splash.conf"
  }
  
  package { 'python-pip':
    ensure => present,
    require => Package["epel-release"],
  }

  exec { 'python-sh':
    command => "pip-python install sh",
    require => Package["python-pip"],
    cwd     => "/root",
  }

}
