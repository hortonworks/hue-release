class prepare{

  ##Redhat bug fix: https://bugzilla.redhat.com/show_bug.cgi?id=805593
  exec{"redhat_huegpage":
    command => "echo never > /sys/kernel/mm/redhat_transparent_hugepage/defrag; echo no > /sys/kernel/mm/redhat_transparent_hugepage/khugepaged/defrag"
  }

  exec{'disable_selinux':
    command => 'echo 0 >/selinux/enforce'
  }

  package{'java':
    provider => rpm, 
    ensure => installed,
    source => "http://dev2.hortonworks.com.s3.amazonaws.com/ARTIFACTS/jdk-7u51-linux-x64.rpm"
  }
  
  service {"iptables":
    enable => false,
    ensure => "stopped"
  }

  service {"ip6tables":
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
