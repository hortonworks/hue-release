class postinstall::solr{

  exec {"download solr":
    command => "wget -O /opt/solr.tar.gz http://mirror.reverse.net/pub/apache/lucene/solr/4.7.2/solr-4.7.2.tgz && tar xvf solr.tar.gz && rm solr.tar.gz",
    cwd => "/opt",
    timeout => 0
  }

  exec{"download lucidworks":
    command => "wget -O /opt/lucidworks-hadoop-lws-job.jar http://dev2.hortonworks.com.s3.amazonaws.com/stuff/lucidworks-hadoop-lws-job-1.3.0.jar",
    timeout => 0
  }

  user {"solr":
    name => "solr",
    ensure => "present",
    password => "solr"
  }
  
  
}
