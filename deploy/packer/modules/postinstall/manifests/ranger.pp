class postinstall::ranger{

  user {"xapolicymgr":
    name => "xapolicymgr",
    password => "xapolicymgr",
    ensure     => "present",
    managehome => true,
  }


  package{"ranger_*":
    ensure => installed,
  }

  file { "ranger_directory":
    path => "/tmp/ranger",
    source => "puppet:///modules/postinstall/ranger/",
    mode   => '777',
    recurse => true,
    require => Package["ranger_*"],
  }

 #   Puppet doesn't like relative path like this
 #   cwd => "puppet:///modules/postinstall/ranger/install_overrides",
  exec{"override_properties_and_install":
    cwd => "/tmp/ranger/install_overrides",
    command => "bash /tmp/ranger/scripts/ranger_override_properties_and_install.sh",
    require => File["ranger_directory"],
    logoutput => true,
    timeout => 1800,
  }

  exec{"ranger_restart_namenode":
    cwd => "/tmp/ranger/scripts",
    command => "bash /tmp/ranger/scripts/restart_namenode.sh",
    require => Exec["override_properties_and_install"],
    logoutput => true,
  }

  exec{"ranger_restart_hiveservers":
    cwd => "/tmp/ranger/scripts",
    command => "bash /tmp/ranger/scripts/restart_hiveservers.sh",
    require => Exec["ranger_restart_namenode"],
    logoutput => true,
  }

  exec{"ranger_restart_hbase":
    cwd => "/tmp/ranger/scripts",
    command => "bash /tmp/ranger/scripts/restart_hbase.sh",
    require => Exec["ranger_restart_hiveservers"],
    logoutput => true,
  }

  file { "stage_create_policies":
    path => "/tmp/create_ranger_policies.sh",
    source => "puppet:///modules/postinstall/ranger/policies/create_ranger_policies.sh",
    mode   => '777',
    require => Exec["ranger_restart_hbase"],
  }

  exec{"create_ranger_policies":
    cwd => "/tmp/ranger/policies",
    command => "/tmp/create_ranger_policies.sh",
    require => [File["stage_create_policies"], File["ranger_directory"]],
    logoutput => true,
    timeout => 0,
  }

  exec{"ranger_create_hue_users":
    cwd => "/tmp/ranger_tutorial/hue",
    command => "/bin/bash /tmp/ranger_tutorial/hue/setup_data.sh",
    require => [Class["postinstall::hue"], Exec["create_ranger_policies"]],
    logoutput => true,
  }

  ambariApi {"restart hbase":
    url => "requests",
    method => "POST",
    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HBASE","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HBASE"}},"Requests/resource_filters":[{"service_name":"HBASE","component_name":"HBASE_CLIENT","hosts":"sandbox.hortonworks.com"},{"service_name":"HBASE","component_name":"HBASE_MASTER","hosts":"sandbox.hortonworks.com"},{"service_name":"HBASE","component_name":"HBASE_REGIONSERVER","hosts":"sandbox.hortonworks.com"}]}',
    require => Exec["override_properties_and_install"],
  }

  ambariApi {"restart hive":
    url => "requests",
    method => "POST",
    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HIVE","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HIVE"}},"Requests/resource_filters":[{"service_name":"HIVE","component_name":"HCAT","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"HIVE_CLIENT","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"HIVE_METASTORE","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"HIVE_SERVER","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"MYSQL_SERVER","hosts":"sandbox.hortonworks.com"},{"service_name":"HIVE","component_name":"WEBHCAT_SERVER","hosts":"sandbox.hortonworks.com"}]}',
    require => Exec["override_properties_and_install"],
  }


#  ambariApi {"maintenance_on":
#    url => "hosts/sandbox.hortonworks.com",
#    method => "PUT",
#    body => '{"RequestInfo":{"context":"Turn On Maintenance Mode for host"},"Body":{"Hosts":{"maintenance_state":"ON"}}}',
#    require => Exec["create_ranger_policies"],
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

#include postinstall::ranger
