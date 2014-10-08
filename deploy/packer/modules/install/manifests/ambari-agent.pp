class install::ambari-agent {

  exec{"ambari-repo":
    command => "wget -O /etc/yum.repos.d/ambari.repo  http://s3.amazonaws.com/dev.hortonworks.com/ambari/centos6/1.x/updates/1.7.0/ambari.repo",
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
