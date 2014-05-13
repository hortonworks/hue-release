class postinstall {

  $services = ["ambari-agent", "ambari-server", "auditd", "cups", "gmetad", "gmond", "hadoop-mapreduce-historyserver", "hadoop-yarn-nodemanager", "hadoop-yarn-proxyserver", "hadoop-yarn-resourcemanager", "hdp-gmetad", "hdp-gmond", "nagios", "nfs", "nfslock", "rpcbind", "rpcidmapd", "rpcgssd", "rpcsvcgssd"]

  $postInstallPackages = ["knox", "yum-plugin-priorities", "epel-release", "libxslt", "python-lxml"]

  package{$postInstallPackages:
    ensure => installed,
    require => Class["install::ambari-bluprints"]
  }

  exec{"install nfs":
    command => "yum install -y nfs*",
  }

  exec{"create knox master":
    command => "su -l knox -c '/usr/lib/knox/bin/knoxcli.sh create-master --master knox'",
    require => Package["knox"]
  }

  service {$services:
    enable => false,
    require => [Package[$postInstallPackages],Exec["install nfs"]]
  }

  include sandbox
}
