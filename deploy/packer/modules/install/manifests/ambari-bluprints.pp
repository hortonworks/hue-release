class install::ambari-bluprints{

  file{"/tmp/install/bluprint-1-node.json":
    source => "puppet:///modules/install/bluprint-1-node.json"
  }

  file{"/tmp/install/cluster-bluprint.json":
    source => "puppet:///modules/install/cluster-bluprint.json"
  }

  file{"/tmp/install/check_status.py":
    source => "puppet:///modules/install/check_status.py" 
  }

  file{"/tmp/install/check_status.sh":
    source => "puppet:///modules/install/check_status.sh" 
  }

  exec {"add bluprint":
    command => "curl -f -H 'X-Requested-By: ambari' -u admin:admin http://127.0.0.1:8080/api/v1/blueprints/single-node-sandbox -d @/tmp/install/bluprint-1-node.json",
    require => [File["/tmp/install/bluprint-1-node.json"],Class["install::ambari-server"]],
    logoutput => true
  }

  exec {"add cluster":
    command => "curl -f -H 'X-Requested-By: ambari' -u admin:admin http://127.0.0.1:8080/api/v1/clusters/Sandbox -d @/tmp/install/cluster-bluprint.json",
    require => [File["/tmp/install/cluster-bluprint.json"],Exec["add bluprint"]],
    logoutput => true
  }

  exec {"install cluster":
    command => "/bin/bash /tmp/install/check_status.sh",
    cwd => "/tmp/install",
    timeout => 0,
    logoutput => true,
    require => [File["/tmp/install/check_status.py"], File["/tmp/install/check_status.sh"], Exec["add cluster"]]
  }
  
}
