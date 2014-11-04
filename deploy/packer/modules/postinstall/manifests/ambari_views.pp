class postinstall::ambari_views{
  class download_ambari_views {

/*
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

    file { 'pig-view-props.json':
      path    => "/tmp/pig-view-props.json",
      content => '[ {
"ViewInstanceInfo" : {
"properties" : {
"dataworker.webhcat.url" : "http://sandbox.hortonworks.com:50111/templeton/v1",
"dataworker.webhcat.user" : "hue",
"dataworker.scripts.path" : "/tmp/.pigscripts",
"dataworker.jobs.path" : "/tmp/.pigjobs",
"dataworker.defaultFs" : "webhdfs://sandbox.hortonworks.com:50070",
"dataworker.username" : "pigview"
}
}
} ]'
    }

    file { 'files-view-props.json':
      path    => "/tmp/files-view-props.json",
      content => '
[ {
"ViewInstanceInfo" : {
"properties" : {
"dataworker.defaultFs" : "hdfs://sandbox.hortonworks.com:8020"
}
}
} ]'
    }

    file { 'capsched-view-props.json':
      path    => "/tmp/capsched-view-props.json",
      content => '[ {
"ViewInstanceInfo" : {
"properties" : {
"ambari.server.url" : "http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox",
"ambari.server.username" : "admin",
"ambari.server.password" : "admin"
}
}
} ]'
    }
*/

    file { 'slider-view-props.json':
      path    => "/tmp/slider-view-props.json",
      content => '[ {
"ViewInstanceInfo" : {
"properties" : {
"ambari.server.url" : "http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox",
"ambari.server.username" : "admin",
"ambari.server.password" : "admin"
}
}
} ]'
    }
  }

  class create_instances {
    include download_ambari_views

    exec {'install_views':
      command => 'ambari-server restart; while ! curl -s --user admin:admin 127.0.0.1:8080/api/v1/views 2>&1 >/dev/null; do sleep 1; done',
      require => Class[download_ambari_views],
    }

/*
    exec {'files_wait_deploy':
      command => 'while curl -s --user admin:admin http://127.0.0.1:8080/api/v1/views/FILES/versions/0.1.0 | grep DEPLOYING >/dev/null; do sleep 1; done',
      require => Exec['install_views'],
      provider => 'shell',
      timeout => 0,
    }

    exec {'files_instance':
      command => 'curl -v -X POST --user admin:admin -H X-Requested-By:ambari 127.0.0.1:8080/api/v1/views/FILES/versions/0.1.0/instances/MyFiles --data "@/tmp/files-view-props.json"',
      require => Exec['files_wait_deploy'],
      provider => 'shell',
      timeout => 0,
    }

    exec {'pig_wait_deploy':
      command => 'while curl -s --user admin:admin http://127.0.0.1:8080/api/v1/views/PIG/versions/0.1.0 | grep DEPLOYING >/dev/null; do sleep 1; done',
      require => Exec['install_views'],
      provider => 'shell',
      timeout => 0,
    }

    exec {'pig_instance':
      command => 'curl -v -X POST --user admin:admin -H X-Requested-By:ambari 127.0.0.1:8080/api/v1/views/PIG/versions/0.1.0/instances/MyPig --data "@/tmp/pig-view-props.json"',
      require => Exec['pig_wait_deploy'],
      provider => 'shell',
      timeout => 0,
    }

    exec {'capsched_wait_deploy':
      command => 'while curl -s --user admin:admin http://127.0.0.1:8080/api/v1/views/CAPACITY-SCHEDULER/versions/0.1.0 | grep DEPLOYING >/dev/null; do sleep 1; done',
      require => Exec['install_views'],
      provider => 'shell',
      timeout => 0,
    }

    exec {'capsched_instance':
      command => 'curl -v -X POST --user admin:admin -H X-Requested-By:ambari 127.0.0.1:8080/api/v1/views/CAPACITY-SCHEDULER/versions/0.1.0/instances/CS_1 --data "@/tmp/capsched-view-props.json"',
      require => Exec['capsched_wait_deploy'],
      provider => 'shell',
      timeout => 0,
    }
*/
    exec {'slider_wait_deploy':
      command => 'while curl -s --user admin:admin http://127.0.0.1:8080/api/v1/views/SLIDER/versions/1.0.0 | grep DEPLOYING >/dev/null; do sleep 1; done',
      require => Exec['install_views'],
      provider => 'shell',
      timeout => 0,
    }


    exec {'slider_instance':
      command => 'curl -v -X POST --user admin:admin -H X-Requested-By:ambari 127.0.0.1:8080/api/v1/views/SLIDER/versions/1.0.0/instances/SLIDER_1 --data "@/tmp/slider-view-props.json"',
      require => Exec['slider_wait_deploy'],
      provider => 'shell',
      timeout => 0,
    }
  }
  include create_instances

  exec {'finish_views_install':
    command => 'ambari-server restart; while ! curl -s --user admin:admin 127.0.0.1:8080/api/v1/views 2>&1 >/dev/null; do sleep 1; done',
    require => Class[create_instances],
  }

}
