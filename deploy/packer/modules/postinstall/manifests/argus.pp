class postinstall::argus{
  
  file {"wait_finish.py":
    path => "/tmp/wait_finish.py",
    source => "puppet:///modules/postinstall/wait_finish.py"
  }
  
  define ambariApi($url, $body, $method = 'POST') {
    case $method {
      POST: {
        exec {"/usr/bin/curl  -H \"X-Requested-By: ambari\"  -u admin:admin -d '${body}' http://127.0.0.1:8080/api/v1/clusters/Sandbox/${url} | python /tmp/wait_finish.py; sleep 5":
        }
      }
      PUT: {
        exec {"/usr/bin/curl  -H \"X-Requested-By: ambari\"  -u admin:admin -X PUT -d '${body}' http://127.0.0.1:8080/api/v1/clusters/Sandbox/${url} | python /tmp/wait_finish.py; sleep 5":
        }
      }
    }
  }
  
  user {"xapolicymgr":
    name => "xapolicymgr",
    password => "xapolicymgr",
    ensure     => "present",
    managehome => true,
  }
  
    
  package{"argus*":
    ensure => installed,
  }


#  file { "/usr/hdp/current/argus/admin/install.properties":
#    source => "puppet:///modules/postinstall/argus/install_overrides/admin/install.properties",
#    require => Package["argus*"],
#    group  => '0',
#    mode   => '777',
#    owner  => '0',
#  }
#
#  file { "/usr/hdp/current/argus/ugsync/install.properties":
#    source => "puppet:///modules/postinstall/argus/install_overrides/ugsync/install.properties",
#    require => Package["argus*"],
#    group  => '0',
#    mode   => '640',
#    owner  => '0',
#  }
#
#  file { "/usr/hdp/current/argus/hdfs-agent/install.properties":
#    source => "puppet:///modules/postinstall/argus/install_overrides/hdfs-agent/install.properties",
#    require => Package["argus*"],
#    group  => '0',
#    mode   => '640',
#    owner  => '0',
#  }
#
#  file { "/usr/hdp/current/argus/hive-agent/install.properties":
#    source => "puppet:///modules/postinstall/argus/install_overrides/hive-agent/install.properties",
#    require => Package["argus*"],
#    group  => '0',
#    mode   => '640',
#    owner  => '0',
#  }
  
  file { "stage_override_properties":
    path => "/tmp/argus_override_properties_and_install.sh",
    source => "puppet:///modules/postinstall/argus/scripts/argus_override_properties_and_install.sh",
    mode   => '777',
    require => Package["argus*"],
  }
 
 #   Puppet doesn't relative like this
 #   cwd => "puppet:///modules/postinstall/argus/install_overrides", 
  exec{"override_properties_and_install":
    cwd => "/vagrant/modules/postinstall/files/argus/install_overrides",
    command => "/tmp/argus_override_properties_and_install.sh",
    require => File["stage_override_properties"],
    logoutput => true,
  }
  
#  exec{"install_argus_admin":
#    cwd => "/usr/hdp/current/argus/admin",
#    command => "/usr/hdp/current/argus/admin/install.sh",
#    require => Exec["override_properties"],
#  }
#  
#  exec{"install_argus_user_sync":
#    cwd => "/usr/hdp/current/argus/ugsync",
#    command => "/usr/hdp/current/argus/ugsync/install.sh",
#    require => Exec["install_argus_admin"],
#  }
#   
#  exec{"install_argus_hdfs_agent":
#    cwd => "/usr/hdp/current/argus/hdfs-agent",
#    command => "/usr/hdp/current/argus/hdfs-agent/enable-hdfs-agent.sh",
#    require => Exec["install_argus_admin"],
#  } 
  
  file { "stage_create_policies":
    path => "/tmp/create_argus_policies.sh",
    source => "puppet:///modules/postinstall/argus/policies/create_argus_policies.sh",
    mode   => '777',
    require => Exec["override_properties_and_install"],
  }
  
  file { "stage_hdfs_repos":
    path => "/tmp/repo_hdfs.json",
    source => "puppet:///modules/postinstall/argus/policies/repo_hdfs.json",
    mode   => '777',
    require => Exec["override_properties_and_install"],
  }
  
   file { "stage_hdfs_policies":
    path => "/tmp/policies_hdfs_public.json",
    source => "puppet:///modules/postinstall/argus/policies/policies_hdfs_public.json",
    mode   => '777',
    require => Exec["override_properties_and_install"],
  }

  exec{"create_argus_policies":
    cwd => "/tmp",
    command => "/tmp/create_argus_policies.sh",
#    require => File["stage_create_policies"],
    require => File["stage_create_policies", "stage_hdfs_repos", "stage_hdfs_policies"],
    logoutput => true,
  }
  ambariApi {"maintenance_on":
    url => "hosts/sandbox.hortonworks.com",
    method => "PUT",
    body => '{"RequestInfo":{"context":"Turn On Maintenance Mode for host"},"Body":{"Hosts":{"maintenance_state":"ON"}}}',
    require => Exec["create_argus_policies"],
  }

  ambariApi {"restart hdfs":
    url => "requests",
    method => "POST",
    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HDFS","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HDFS"}},"Requests/resource_filters":[{"service_name":"HDFS","component_name":"DATANODE","hosts":"sandbox.hortonworks.com"},{"service_name":"HDFS","component_name":"HDFS_CLIENT","hosts":"sandbox.hortonworks.com"},{"service_name":"HDFS","component_name":"NAMENODE","hosts":"sandbox.hortonworks.com"},{"service_name":"HDFS","component_name":"SECONDARY_NAMENODE","hosts":"sandbox.hortonworks.com"}]}',
    require => AmbariApi["maintenance_on"],
  }

  ambariApi {"maintenance_off":
    url => "hosts/sandbox.hortonworks.com",
    method => "PUT",
    body => '{"RequestInfo":{"context":"Turn Off Maintenance Mode for host"},"Body":{"Hosts":{"maintenance_state":"OFF"}}}',
    require => AmbariApi["restart hdfs"],
  }

}

#include postinstall::argus
