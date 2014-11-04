class prepare{

  package{"java":
    name => "java-1.7.0-openjdk-devel",
    ensure => installed
  }
  
  # package{'java':
  #   provider => rpm, 
  #   ensure => installed,
  #   source => "http://dev2.hortonworks.com.s3.amazonaws.com/ARTIFACTS/jdk-7u51-linux-x64.rpm"    
  # }

  $iptable = ["iptables", "ip6tables"]
  
  service {$iptables:
    enable => false,
    ensure => "stopped"
  }

  package {'wget':
    ensure => installed
  }

  exec{'set_javahome':    
    command => "echo 'export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk.x86_64; export PATH=\$JAVA_HOME/bin:\$PATH' > /etc/profile.d/java.sh;",
    require => Package['java']
  }
 
  ###Because of ambari fails due to timeout need to preinstall all the software.
  #if $role == 'ambari' {
  #  exec {"preinstall software":
  #    command => 'wget -O /etc/yum.repos.d/HDP.repo http://dev.hortonworks.com.s3.amazonaws.com/HDP/centos6/2.x/updates/2.2.0.0/hdp.repo && yum install -y hadoop hadoop-yarn hive pig webhcat-tar-pig webhcat-tar-hive falcon sqoop oozie tez zookeeper mysql-connector-java storm hive-hcatalog hive-webhcat hbase && rm -rf /etc/yum.repos.d/HDP.repo',
  #    timeout => 0
  #  }
  #}
  #else {
  #  exec {"preinstall software":
  #    command => 'wget -O /etc/yum.repos.d/HDP.repo http://dev.hortonworks.com.s3.amazonaws.com/HDP/centos6/2.x/updates/2.2.0.0/hdp.repo && yum install -y hadoop hadoop-yarn hive pig oozie-client tez hbase-client mysql-connector-java zookeeper && rm -rf /etc/yum.repos.d/HDP.repo',
  #    timeout => 0
  #  }    
  #}

  file {"wait_finish.py":
    path => "/tmp/wait_finish.py",
    source => "puppet:///modules/prepare/wait_finish.py"
  }

  file {"/var/cache/wget":
    ensure => directory,
    replace => false
  }
}

