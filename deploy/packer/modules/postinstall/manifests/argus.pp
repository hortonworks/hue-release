class postinstall::argus{
  
  user {"xapolicymgr":
    name => "xapolicymgr",
    password => "xapolicymgr",
    ensure     => "present",
    managehome => true,
  }
  
  
  package{"argus_*":
    ensure => installed,
  }

  file { "argus_directory":
    path => "/tmp/argus",
    source => "puppet:///modules/postinstall/argus/",
    mode   => '777',
    recurse => true,
    require => Package["argus_*"],
  }
 
 #   Puppet doesn't like relative path like this
 #   cwd => "puppet:///modules/postinstall/argus/install_overrides", 
  exec{"override_properties_and_install":
    cwd => "/tmp/argus/install_overrides",
    command => "bash /tmp/argus/scripts/argus_override_properties_and_install.sh",
    require => File["argus_directory"],
    logoutput => true,
  }

  exec{"argus_restart_namenode":
    cwd => "/tmp/argus/scripts",
    command => "bash /tmp/argus/scripts/restart_namenode.sh",
    require => Exec["override_properties_and_install"],
    logoutput => true,
  }

  exec{"argus_restart_hiveservers":
    cwd => "/tmp/argus/scripts",
    command => "bash /tmp/argus/scripts/restart_hiveservers.sh",
    require => Exec["argus_restart_namenode"],
    logoutput => true,
  }

  exec{"argus_restart_hbase":
    cwd => "/tmp/argus/scripts",
    command => "bash /tmp/argus/scripts/restart_hbase.sh",
    require => Exec["argus_restart_hiveservers"],
    logoutput => true,
  }
  
  file { "stage_create_policies":
    path => "/tmp/create_argus_policies.sh",
    source => "puppet:///modules/postinstall/argus/policies/create_argus_policies.sh",
    mode   => '777',
    require => Exec["argus_restart_hbase"],
  }
  
  exec{"create_argus_policies":
    cwd => "/tmp/argus/policies",
    command => "/tmp/create_argus_policies.sh",
    require => [File["stage_create_policies"], File["argus_directory"]],    
    logoutput => true,
  }
  
#  ambariApi {"maintenance_on":
#    url => "hosts/sandbox.hortonworks.com",
#    method => "PUT",
#    body => '{"RequestInfo":{"context":"Turn On Maintenance Mode for host"},"Body":{"Hosts":{"maintenance_state":"ON"}}}',
#    require => Exec["create_argus_policies"],
#  }
#
#  ambariApi {"restart hdfs":
#    url => "requests",
#    method => "POST",
#    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HDFS","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HDFS"}},"Requests/resource_filters":[{"service_name":"HDFS","component_name":"NAMENODE","hosts":"sandbox.hortonworks.com"}]}',
#    require => AmbariApi["maintenance_on"],
#  }
#
#  ambariApi {"restart hive":
#    url => "requests",
#    method => "POST",
#    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HIVE","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HIVE"}},"Requests/resource_filters":[{"service_name":"HIVE","component_name":"HCAT","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"HIVE_CLIENT","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"HIVE_METASTORE","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"HIVE_SERVER","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"MYSQL_SERVER","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"WEBHCAT_SERVER","hosts":"sandbox.hortonworks.com"}]}',
#    require => AmbariApi["restart hdfs"],
#  }
#
#  ambariApi {"restart hbase":
#    url => "requests",
#    method => "POST",
#    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HBase","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HBASE"}},"Requests/resource_filters":[{"service_name":"HBASE","component_name":"MASTERSERVER","hosts":"sandbox.hortonworks.com"}, {"service_name":"HBASE","component_name":"REGIONSERVER","hosts":"sandbox.hortonworks.com"}]}',
#    require => AmbariApi["restart hive"],
#  }
#
#  ambariApi {"maintenance_off":
#    url => "hosts/sandbox.hortonworks.com",
#    method => "PUT",
#    body => '{"RequestInfo":{"context":"Turn Off Maintenance Mode for host"},"Body":{"Hosts":{"maintenance_state":"OFF"}}}',
#    require => AmbariApi["restart hbase"],
#  }

}

#include postinstall::argus
