class postinstall::accumulo{
  
  if $role == 'ambari' {
    include install::ambari-bluprints
    exec{"install accumulo":
      command => "yum install -y accumulo",
      timeout =>0,
      require => Class["install::ambari-bluprints"]
    }
  } 
  else {
    include install::finish-cluster
    exec{"install accumulo":
      command => "yum install -y accumulo",
      timeout =>0,
      require => Class["install::finish-cluster"]
    }
  }
  

}
