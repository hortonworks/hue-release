class postinstall::kafka{

  package{"kafka":
    provider => rpm,
    ensure => installed,
    source => "http://public-repo-1.hortonworks.com/HDP-LABS/Projects/kafka/0.8.1/centos6/kafka-0.8.1.2.1.4.0-632.el6.noarch.rpm",
    require => Class["install::ambari-bluprints"]
  }


}
