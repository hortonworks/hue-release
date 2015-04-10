class postinstall::solr{

  user {"solr":
    name => "solr",
    password => "solr",
    ensure     => "present",
    managehome => true
  }

  file {"/opt/solr":
    ensure => directory,
    owner => "solr"
  }

  # exec {"chown solr":
  #   command => "chown solr /opt/solr",
  #   require => [File["/opt/solr"]],
  # }

  exec {"download solr":
    command => "wget -N -P /var/cache/wget http://mirror.reverse.net/pub/apache/lucene/solr/4.10.4/solr-4.10.4.tgz && cp /var/cache/wget/solr*.tgz ./solr.tar.gz && tar xvf solr.tar.gz && rm solr.tar.gz",
    cwd => "/opt/solr",
    require => [File["/opt/solr"]],
    timeout => 200,
    creates => "/opt/solr/solr-4.10.4"
  }

  exec {"download lucidworks-hadoop":
    command => "wget -N -P /var/cache/wget http://dev2.hortonworks.com.s3.amazonaws.com/stuff/lucidworks-hadoop-lws-job-1.3.0.jar && cp /var/cache/wget/lucidworks-hadoop-lws-job-1.3.0.jar ./",
    cwd => "/opt/solr",
    require => [File["/opt/solr"]],
    timeout => 200,
    creates => "/opt/solr/lucidworks-hadoop-lws-job-1.3.0.jar"
  }

  exec {"prepare_solr":
    command => "/bin/bash /tmp/install/solr_prepare.sh",
    require => [File["/tmp/install/solr_prepare.sh"],Exec["download solr"],Exec["download lucidworks-hadoop"]],  # ,Class["install::ambari-bluprints"]
    timeout => 200
  }

  
  file { "/tmp/install/solr_prepare.sh":
    source => "puppet:///modules/postinstall/solr/solr_prepare.sh"
  }

  file { "/opt/solr/solr/hdp/solr/hdp1/conf/solrconfig.xml":
    source => "puppet:///modules/postinstall/solr/solrconfig.xml",
    require => [Exec["prepare_solr"]],
  }

  file { "/opt/solr/solr/hdp/solr/hdp1/conf/schema.xml":
    source => "puppet:///modules/postinstall/solr/schema.xml",
    require => [Exec["prepare_solr"]],
  }

  file { 'start_solr':
    path    => "/root/start_solr.sh",
    source => "puppet:///modules/postinstall/solr/start_solr.sh",
    mode => 777
  }

  file { 'stop_solr':
    path    => "/root/stop_solr.sh",
    source => "puppet:///modules/postinstall/solr/stop_solr.sh",
    mode => 777
  }  
}
