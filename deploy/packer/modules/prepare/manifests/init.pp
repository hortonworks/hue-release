class prepare{
  
  exec{'disable_selinux':
    command => 'echo 0 >/selinux/enforce'
  }

  package{'java':
    provider => rpm, 
    ensure => installed,
    source => "http://dev2.hortonworks.com.s3.amazonaws.com/ARTIFACTS/jdk-7u51-linux-x64.rpm"
  }

  $iptable = ["iptables", "ip6tables"]
  
  service {$iptables:
    enable => false,
    ensure => "stopped"
  }

  package {'wget':
    ensure => installed
  }

  exec{'set_javahome':
    command => "echo 'export JAVA_HOME=/usr/java/jdk1.7.0_51; export PATH=\$JAVA_HOME/bin:\$PATH' > /etc/profile.d/java.sh;",
    require => Package['java']
  }
  
}
