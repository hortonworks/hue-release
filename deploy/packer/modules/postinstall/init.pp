class postinstall {

  $services = ["ambari-agent", "ambari-server", "auditd", "cups", "gmetad", "gmond", "hadoop-mapreduce-historyserver", "hadoop-yarn-nodemanager", "hadoop-yarn-proxyserver", "hadoop-yarn-resourcemanager", "hdp-gmetad", "hdp-gmond", "nagios", "nfs", "nfslock", "rpcbind", "rpcidmapd", "rpcgssd", "rpcsvcgssd"]

  service {$services:
    enable => false,
    require => Class["install"]
  }
}
