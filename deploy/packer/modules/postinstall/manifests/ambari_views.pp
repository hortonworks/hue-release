class postinstall::ambari_views{
  class download_ambari_views {
    exec {"files":
      command => "wget -O /var/lib/ambari-server/resources/views/files-0.1.0-SNAPSHOT.jar http://dev2.hortonworks.com.s3.amazonaws.com/ARTIFACTS/views/files-0.1.0-SNAPSHOT.jar",
      timeout => 0,
      creates => "/var/lib/ambari-server/resources/views/files-0.1.0-SNAPSHOT.jar"
    }

    exec {"pig":
      command => "wget -O /var/lib/ambari-server/resources/views/pig-0.1.0-SNAPSHOT.jar http://dev2.hortonworks.com.s3.amazonaws.com/ARTIFACTS/views/pig-0.1.0-SNAPSHOT.jar",
      timeout => 0,
      creates => "/var/lib/ambari-server/resources/views/pig-0.1.0-SNAPSHOT.jar"
    }

    exec {"capacity-scheduler":
      command => "wget -O /var/lib/ambari-server/resources/views/capacity-scheduler-0.0.1-SNAPSHOT.jar http://dev2.hortonworks.com.s3.amazonaws.com/ARTIFACTS/views/capacity-scheduler-0.0.1-SNAPSHOT.jar",
      timeout => 0,
      creates => "/var/lib/ambari-server/resources/views/capacity-scheduler-0.0.1-SNAPSHOT.jar"
    }
  }
  include download_ambari_views

  exec {'restart ambari':
    command => 'ambari-server restart',
    require => Class[download_ambari_views],
  }
}
