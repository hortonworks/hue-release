class install::ambari-agent {

  exec{"ambari-repo":
    command => "wget -O /etc/yum.repos.d/ambari.repo http://public-repo-1.hortonworks.com.s3.amazonaws.com/HDP/centos6/2.x/GA/2.2.0.0/hdp.repo",
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

  exec {"ambari-agent start":
    command => "ambari-agent start",
    require => [Exec["register ambari agent"]],
    returns => [0, 255]  # 255 means already started
  }

}
