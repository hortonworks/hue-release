class postinstall::splash {

  file { 'ttys':
    path    => "/etc/init/start-ttys.override",
    source => "puppet:///modules/postinstall/tty/start-ttys.override"
  }

  file { 'tty1':
    path    => "/etc/init/tty-splash.conf",
    source => "puppet:///modules/postinstall/tty/tty-splash.conf"
  }

  exec { 'tty bashrc':
    command => "echo '[[ $(tty) = \"/dev/tty1\" ]] && bash /usr/lib/hue/tools/start_scripts/post_start.sh' >> /root/.bashrc",
    require => Package["hue-sandbox"]
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

  exec { 'splash':
    command => "initctl stop tty TTY=/dev/tty1; initctl start tty-splash TTY=/dev/tty1; true",
    require => Exec["tty bashrc"]
  }

}
