class splash{
  file { 'ttys':
    path    => "/etc/init/tty-splash.conf",
    content => "stop on runlevel [S016]

    respawn
    instance $TTY
    exec /sbin/mingetty --autologin root --noclear $TTY"
  }

  file { 'tty1':
    path    => "/etc/init/start-ttys.conf",
    source => "puppet:///modules/postinstall/splash/start-ttys.conf"
  }

  file { 'bashrc':
    path    => "/root/.bashrc",
    source => "puppet:///modules/postinstall/splash/bashrc"
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
    require => [File["tty1"],File["ttys"], File["bashrc"], Exec["python-sh"],Package["hue-sandbox"]],
  }

  
}

class postinstall::sandbox{

  yumrepo{"sandbox":
    baseurl => "http://dev2.hortonworks.com.s3.amazonaws.com/repo/dev/baikal-GA-2.3.1/utils/",
    descr => "Sandbox repository (tutorials)",
    enabled => 1,
    gpgcheck => 0,
    require => Class["postinstall"]
  }

  $services = ["ambari-agent", "ambari-server", "auditd", "cups", "gmetad", "gmond", "hadoop-mapreduce-historyserver", "hadoop-yarn-nodemanager", "hadoop-yarn-proxyserver", "hadoop-yarn-resourcemanager", "hdp-gmetad", "hdp-gmond", "iptables", "nagios", "nfs", "nfslock", "rpcbind", "rpcidmapd", "rpcgssd", "rpcsvcgssd"]

  $postInstallPackages = ["yum-plugin-priorities", "epel-release", "libxslt", "python-lxml"]

  package{$postInstallPackages:
    ensure => installed,
    require => Class["install::ambari-bluprints"]
  }

  exec{"install nfs":
    command => "yum install -y nfs*",
  }

  service {$services:
    enable => false,
    require => [Package[$postInstallPackages],Exec["install nfs"]]
  }

  $hueSandbox = ["hue-sandbox", "hue-tutorials"]

  package{$hueSandbox:
    ensure => installed,
    require => [Yumrepo["sandbox"],Class["postinstall::hue"]]
  }

  exec { 'hue_password':
    command => "echo 'hue:hadoop' | chpasswd",
    require => Class['postinstall::hue']
  }

  exec { 'hue_sudoers':
    command => "echo -e 'hue ALL=(ALL) ALL\nhue ALL=(ALL) NOPASSWD: /sbin/chkconfig\nhue ALL=(ALL) NOPASSWD: /sbin/service\nhue ALL=(ALL) NOPASSWD: /bin/kill' >> /etc/sudoers",
    require => Class['postinstall::hue']
  }

  file { "/tmp/install/ambari-url-fix.sh":
    source => "puppet:///modules/postinstall/ambari-url-fix.sh"
  }

  exec {'ambari-url-fix.sh':
    command => '/bin/bash /tmp/install/ambari-url-fix.sh',
    require => [File["/tmp/install/ambari-url-fix.sh"], Class["install::ambari-server"]]
  }

  include splash

}
