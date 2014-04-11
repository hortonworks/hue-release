class postinstall {

  $services = ["ambari-agent", "ambari-server", "auditd", "cups", "gmetad", "gmond", "hadoop-mapreduce-historyserver", "hadoop-yarn-nodemanager", "hadoop-yarn-proxyserver", "hadoop-yarn-resourcemanager", "hdp-gmetad", "hdp-gmond", "nagios", "nfs", "nfslock", "rpcbind", "rpcidmapd", "rpcgssd", "rpcsvcgssd"]

  $postInstallPackages = ["hue", "knox"]

  package{$postInstallPackages:
    ensure => installed,
    require => Class["install::ambari-bluprints"]
  }

  exec{"install nfs":
    command => "yum install -y nfs*",
  }

  service {$services:
    enable => false,
    require => [Package[$postInstallPackages],Exec["install nfs"]]
  }

}
