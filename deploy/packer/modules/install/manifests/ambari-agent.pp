class install::ambari-agent {

  exec{"ambari-repo":
    command => "wget -O /etc/yum.repos.d/ambari.repo  http://public-repo-1.hortonworks.com/ambari/centos6/1.x/updates/1.6.1/ambari.repo",
    require => Package["wget"],
    unless => "ls -al /etc/yum.repos.d/ambari.repo"
  }


  package {"ambari-agent":
    ensure => installed,
    require => Exec["ambari-repo"]
  }

  if $sandbox=='true'{
    exec {"register ambari agent":
      command => 'sed -i.bak "/^hostname/ s/.*/hostname=sandbox.hortonworks.com/" /etc/ambari-agent/conf/ambari-agent.ini',
      require => Package["ambari-agent"]
    }
  }
  else
  {
    exec {"register ambari agent":
      command => 'sed -i.bak "/^hostname/ s/.*/hostname=ambari.hortonworks.com/" /etc/ambari-agent/conf/ambari-agent.ini',
      require => Package["ambari-agent"]
    }
  }

  ###Because of ambari fails due to timeout need to preinstall all the software.
   if $role == 'ambari' {
     exec {"preinstall software":
       command => 'yum clean all && wget -O /etc/yum.repos.d/HDP.repo http://dev.hortonworks.com.s3.amazonaws.com/HDP/centos6/2.x/updates/2.1.3.0/hdp.repo && yum install -y hadoop hadoop-yarn hive pig webhcat-tar-pig webhcat-tar-hive falcon sqoop oozie tez zookeeper mysql-connector-java hue knox storm hive-hcatalog hive-webhcat hbase && rm -rf /etc/yum.repos.d/HDP.repo',
       require => Package["ambari-agent"],
       timeout => 0
     }
   }
   else {
     exec {"preinstall software":
       command => 'wget -O /etc/yum.repos.d/HDP.repo http://dev.hortonworks.com.s3.amazonaws.com/HDP/centos6/2.x/updates/2.1.3.0/hdp.repo && yum install -y hadoop hadoop-yarn hive pig oozie-client tez hbase-client mysql-connector-java zookeeper && rm -rf /etc/yum.repos.d/HDP.repo',
       require => Package["ambari-agent"],
       timeout => 0
     }    
   }


    
  exec {"ambari-agent start":
    command => "ambari-agent start",
    require => [Exec["register ambari agent"],Exec["preinstall software"]]
  }

}
