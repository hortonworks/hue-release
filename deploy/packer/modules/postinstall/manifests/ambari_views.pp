class postinstall::ambari_views{
  include download_ambari_views
  include create_instances
  include create_users
  include finish_install
  
  Class['download_ambari_views']->
  Class['create_instances']->
  Class['create_users']->
  Class['finish_install']
}
  class download_ambari_views($files_jar, $pig_jar, $cs_jar, $hive_jar) {
    
    exec {"files":
      command => "/usr/bin/wget --directory-prefix='/var/lib/ambari-server/resources/views/' $files_jar",
      timeout => 0,
    }

    exec {"pig":
      command => "/usr/bin/wget --directory-prefix='/var/lib/ambari-server/resources/views/' $pig_jar",
      timeout => 0,
    }

    exec {"capacity-scheduler":
      command => "/usr/bin/wget --directory-prefix='/var/lib/ambari-server/resources/views/' $cs_jar",
      timeout => 0,
    }
# no download link available so using it from a local file
    exec {"hive":
      command => "/usr/bin/wget --directory-prefix='/var/lib/ambari-server/resources/views/' $hive_jar",
      timeout => 0,
      }
    file { 'pig-view-props.json':
        path    => "/tmp/pig-view-props.json",
        source => "puppet:///modules/postinstall/ambari_views/pig-view-props.json"
    }

    file { 'files-view-props.json':
        path    => "/tmp/files-view-props.json",
        source => "puppet:///modules/postinstall/ambari_views/files-view-props.json"
    }
    file { 'hive-view-props.json':
        path  =>  "/tmp/hive-view-props.json",
        source => "puppet:///modules/postinstall/ambari_views/hive-view-props.json"
    }
    file { 'capsched-view-props.json':
        path    => "/tmp/capsched-view-props.json",
        source => "puppet:///modules/postinstall/ambari_views/capsched-view-props.json"
    }
    file { 'slider-view-props.json':
        path    => "/tmp/slider-view-props.json",
        source => "puppet:///modules/postinstall/ambari_views/slider-view-props.json"
    }
### will add users now to views
    file {'users.json':
        path  =>  "/tmp/users.json",
        source => "puppet:///modules/postinstall/ambari_views/users.json"
    }
    file {'groups.json':
        path  => "/tmp/groups.json",
        source => "puppet:///modules/postinstall/ambari_views/groups.json"
    }
    file {'adduserstogroup.json':
      path  => "/tmp/adduserstogroup.json",
      source => "puppet:///modules/postinstall/ambari_views/adduserstogroup.json"
    }
    file {'addgrouptoview.json':
      path  => "/tmp/addgrouptoview.json",
      source  => 'puppet:///modules/postinstall/ambari_views/addgrouptoview.json'
    }
		file {'tez.json':
			path	=> "/tmp/tez.json",
			source	=> 'puppet:///modules/postinstall/ambari_views/tez.json'
		}
}

class create_instances{

  exec {'install_views':
      command => '/usr/sbin/ambari-server restart; while ! curl -s --user admin:admin 127.0.0.1:8080/api/v1/views 2>&1 >/dev/null; do sleep 1; done',
      require => Class[download_ambari_views],
    }


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
      command => 'curl -v -X POST --user admin:admin -H X-Requested-By:ambari 127.0.0.1:8080/api/v1/views/CAPACITY-SCHEDULER/versions/0.3.0/instances/CS_1 --data "@/tmp/capsched-view-props.json"',
      require => Exec['capsched_wait_deploy'],
      provider => 'shell',
      timeout => 0,
    }
  exec {'hive_wait_deploy':
      command => 'while curl -s --user admin:admin http://127.0.0.1:8080/api/v1/views/HIVE/versions/0.2.0 | grep DEPLOYING >/dev/null; do sleep 1; done',
      require => Exec['install_views'],
      provider => 'shell',
      timeout => 0,
  }

  exec {'hive_instance':
      command => 'curl -v -X POST --user admin:admin -H X-Requested-By:ambari 127.0.0.1:8080/api/v1/views/HIVE/versions/0.2.0/instances/MyHive --data "@/tmp/hive-view-props.json"',
      require => Exec['hive_wait_deploy'],
      provider => 'shell',
      timeout => 0,
  }


  exec {'slider_wait_deploy':
    command => 'while curl -s --user admin:admin http://127.0.0.1:8080/api/v1/views/SLIDER/versions/1.0.0 | grep DEPLOYING >/dev/null; do sleep 1; done',
    require => Exec['install_views'],
    provider => 'shell',
    timeout => 0,
  }

	exec {'tez_instance':
		command => 'curl -v -X POST --user admin:admin -H X-Requested-By:ambari http://127.0.0.1:8080/api/v1/views/TEZ/versions/0.5.2.2.2.2.0-1238/instances/MyTez --data "@/tmp/tez.json"',
		provider	=> 'shell',
		require => Exec['install_views']
	}	

  exec {'slider_instance':
    command => 'curl -v -X POST --user admin:admin -H X-Requested-By:ambari 127.0.0.1:8080/api/v1/views/SLIDER/versions/1.0.0/instances/SLIDER_1 --data "@/tmp/slider-view-props.json"',
    require => Exec['slider_wait_deploy'],
    provider => 'shell',
    timeout => 0,
  }
}

class  create_users{
  exec {'create_users':
    command => 'curl -H "X-Requested-By: ambari" -X POST -u admin:admin http://localhost:8080/api/v1/users -d @/tmp/users.json',
    provider => 'shell',
    require => Class['create_instances'],
  }
  exec {'create_group':
    command => 'curl -v -H "X-Requested-By: ambari" -X POST -u admin:admin http://localhost:8080/api/v1/groups -d @/tmp/groups.json',
    require => Exec['create_users'],
    provider => 'shell',
  }
  exec {'add_users_to_group':
    command => 'curl -v -H "X-Requested-By: ambari" -X PUT -u admin:admin http://localhost:8080/api/v1/groups/views/members -d @/tmp/adduserstogroup.json',
    require => Exec['create_group'],
    provider => 'shell',
  }
  exec {'add_group_to_CS':
    command => 'curl -v -H "X-Requested-By: ambari" -X PUT -u admin:admin http://localhost:8080/api/v1/views/CAPACITY-SCHEDULER/versions/0.3.0/instances/CS_1/privileges -d @/tmp/addgrouptoview.json',
    require => Exec['add_users_to_group'],
    provider => 'shell',
  }
  exec {'add_group_to_files':
    command => 'curl -v -H "X-Requested-By: ambari" -X PUT -u admin:admin http://localhost:8080/api/v1/views/FILES/versions/0.1.0/instances/MyFiles/privileges -d @/tmp/addgrouptoview.json',
    require => Exec['add_users_to_group'],
    provider => 'shell',
  }
  exec {'add_group_to_hive':
    command => 'curl -v -H "X-Requested-By: ambari" -X PUT -u admin:admin http://localhost:8080/api/v1/views/HIVE/versions/0.0.1/instances/MyHive/privileges -d @/tmp/addgrouptoview.json',
    require => Exec['add_users_to_group'],
    provider => 'shell',
  }
  exec {'add_group_to_pig':
    command => 'curl -v -H "X-Requested-By: ambari" -X PUT -u admin:admin http://localhost:8080/api/v1/views/PIG/versions/0.1.0/instances/MyPig/privileges -d @/tmp/addgrouptoview.json',
    require => Exec['add_users_to_group'],
    provider => 'shell',
  }
  exec {'add_group_to_slider':
    command => 'curl -v -H "X-Requested-By: ambari" -X PUT -u admin:admin http://localhost:8080/api/v1/views/SLIDER/versions/1.0.0/instances/SLIDER_1/privileges -d @/tmp/addgrouptoview.json',
    require => Exec['add_users_to_group'],
    provider => 'shell',
  }
}

class finish_install{
 exec {'finish_views_install':
    command => '/usr/sbin/ambari-server restart; while ! curl -s --user admin:admin 127.0.0.1:8080/api/v1/views 2>&1 >/dev/null; do sleep 1; done',
    require => Class[create_instances]
  }
}
include postinstall::ambari_views
