define sed($line, $replace, $file) {
  exec {"sed -i.bak -r 's/${line}/${replace}/' ${file}": }
}

define line($file, $line, $ensure = 'present') {
    case $ensure {
        default : { err ( "unknown ensure value ${ensure}" ) }
        present: {
            exec { "/bin/echo '${line}' >> '${file}'":
                unless => "/bin/grep -qFx '${line}' '${file}'"
            }
        }
        absent: {
            exec { "/usr/bin/perl -ni -e 'print unless /^\\Q${line}\\E\$/' '${file}'":
                onlyif => "/bin/grep -qFx '${line}' '${file}'"
            }
        }
    }
}

class postinstall::prepare-xasecure {
  file {"/tmp/xasecure":
    ensure => directory,
    owner => "root"
  }

  file {"wait_finish.py":
    path => "/tmp/wait_finish.py",
    source => "puppet:///modules/postinstall/wait_finish.py"
  }

  $downloads = ['policymgr', 'hadoop', 'hbase', 'hive']

  define downloadComponent {
    exec {"download $name":
      command => "wget -O /tmp/xasecure/xasecure-$name.tar http://dev2.hortonworks.com.s3.amazonaws.com/stuff/ambari_stuff/xasecure/xasecure-$name-${xasecure_version}-release.tar && tar xvf xasecure-$name.tar && rm xasecure-$name.tar",
      cwd => "/tmp/xasecure",
      require => [File["/tmp/xasecure"]],
      timeout => 0,
      creates => "/tmp/xasecure/xasecure-$name-${xasecure_version}-release"
    }
  }

  file { "/tmp/xasecure/initial.sql":
    source => "puppet:///modules/postinstall/xasecure/initial.sql"
  }

  downloadComponent { $downloads: }

  user {"policymgr":
    name => "policymgr",
    password => "policymgr",
    ensure     => "present",
    managehome => true
  }
}

class postinstall::xa-policymgr {
  require postinstall::prepare-xasecure

  class properties {
    require postinstall::prepare-xasecure

    sed {'policymgr-db_root_password':
      line    => '^db_root_password=$',
      replace => 'db_root_password=hadoop',
      file => "/tmp/xasecure/xasecure-policymgr-${xasecure_version}-release/install.properties",
    }

    sed {'policymgr-db_password':
      line    => '^db_password=$',
      replace => 'db_password=hadoop',
      file => "/tmp/xasecure/xasecure-policymgr-${xasecure_version}-release/install.properties",
    }

    sed {'policymgr-audit_db_password':
      line    => '^audit_db_password=$',
      replace => 'audit_db_password=hadoop',
      file => "/tmp/xasecure/xasecure-policymgr-${xasecure_version}-release/install.properties",
    }
  }
  include properties

  exec {"install-policymgr":
    command => "bash /tmp/xasecure/xasecure-policymgr-${xasecure_version}-release/install.sh",
    cwd => "/tmp/xasecure/xasecure-policymgr-${xasecure_version}-release",
    timeout => 0,
    environment => ["JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk.x86_64"],
    require => [Class[properties]]
  }

  exec {"load-initial-sql":
    command => "cat /tmp/xasecure/initial.sql | mysql xasecure",
    cwd => "/tmp/xasecure/xasecure-policymgr-${xasecure_version}-release",
    timeout => 0,
    require => Exec["install-policymgr"]
  }
}

class postinstall::xa-hadoop {
  require postinstall::prepare-xasecure

  class properties {
    require postinstall::prepare-xasecure
    sed {'hadoop-POLICY_MGR_URL':
      line    => '^POLICY_MGR_URL=$',
      replace => 'POLICY_MGR_URL=http:\/\/sandbox.hortonworks.com:6080',
      file => "/tmp/xasecure/xasecure-hadoop-${xasecure_version}-release/install.properties",
    }

    sed {'hadoop-REPOSITORY_NAME':
      line    => '^REPOSITORY_NAME=$',
      replace => 'REPOSITORY_NAME=Sandbox_HDFS',
      file => "/tmp/xasecure/xasecure-hadoop-${xasecure_version}-release/install.properties",
    }

    sed {'hadoop-XAAUDIT.DB.HOSTNAME':
      line    => '^XAAUDIT.DB.HOSTNAME=$',
      replace => 'XAAUDIT.DB.HOSTNAME=localhost',
      file => "/tmp/xasecure/xasecure-hadoop-${xasecure_version}-release/install.properties",
    }
    sed {'hadoop-XAAUDIT.DB.DATABASE_NAME':
      line    => '^XAAUDIT.DB.DATABASE_NAME=$',
      replace => 'XAAUDIT.DB.DATABASE_NAME=xasecure',
      file => "/tmp/xasecure/xasecure-hadoop-${xasecure_version}-release/install.properties",
    }
    sed {'hadoop-XAAUDIT.DB.USER_NAME':
      line    => '^XAAUDIT.DB.USER_NAME=$',
      replace => 'XAAUDIT.DB.USER_NAME=xalogger',
      file => "/tmp/xasecure/xasecure-hadoop-${xasecure_version}-release/install.properties",
    }
    sed {'hadoop-XAAUDIT.DB.PASSWORD':
      line    => '^XAAUDIT.DB.PASSWORD=$',
      replace => 'XAAUDIT.DB.PASSWORD=hadoop',
      file => "/tmp/xasecure/xasecure-hadoop-${xasecure_version}-release/install.properties",
    }
  }
  include properties

  exec {"install-hadoop":
    command => "bash /tmp/xasecure/xasecure-hadoop-${xasecure_version}-release/install.sh",
    cwd => "/tmp/xasecure/xasecure-hadoop-${xasecure_version}-release",
    timeout => 0,
    environment => ["JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk.x86_64"],
    require => [Class[properties]]
  }

  ambariApi {"maintenance_on":
    url => "hosts/sandbox.hortonworks.com",
    method => "PUT",
    body => '{"RequestInfo":{"context":"Turn On Maintenance Mode for host"},"Body":{"Hosts":{"maintenance_state":"ON"}}}',
    require => Exec["install-hadoop"]
  }

  line {"source xasecure-hadoop-env.sh":
    file => "/usr/lib/hadoop/libexec/hadoop-config.sh",
    line => '[ -f \$\{HADOOP_CONF_DIR\}/xasecure-hadoop-env.sh ] && source \$\{HADOOP_CONF_DIR\}/xasecure-hadoop-env.sh',
    require => AmbariApi["maintenance_on"]
  }

  ambariApi {"restart hdfs":
    url => "requests",
    method => "POST",
    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HDFS","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HDFS"}},"Requests/resource_filters":[{"service_name":"HDFS","component_name":"DATANODE","hosts":"sandbox.hortonworks.com"},{"service_name":"HDFS","component_name":"HDFS_CLIENT","hosts":"sandbox.hortonworks.com"},{"service_name":"HDFS","component_name":"NAMENODE","hosts":"sandbox.hortonworks.com"},{"service_name":"HDFS","component_name":"SECONDARY_NAMENODE","hosts":"sandbox.hortonworks.com"}]}',
    require => Line["source xasecure-hadoop-env.sh"]
  }

  ambariApi {"maintenance_off":
    url => "hosts/sandbox.hortonworks.com",
    method => "PUT",
    body => '{"RequestInfo":{"context":"Turn Off Maintenance Mode for host"},"Body":{"Hosts":{"maintenance_state":"OFF"}}}',
    require => AmbariApi["restart hdfs"]
  }

}

class postinstall::xa-hive {
  require postinstall::prepare-xasecure

  class properties {
    require postinstall::prepare-xasecure
    sed {'hive-POLICY_MGR_URL':
      line    => '^POLICY_MGR_URL=$',
      replace => 'POLICY_MGR_URL=http:\/\/sandbox.hortonworks.com:6080',
      file => "/tmp/xasecure/xasecure-hive-${xasecure_version}-release/install.properties",
    }

    sed {'hive-REPOSITORY_NAME':
      line    => '^REPOSITORY_NAME=$',
      replace => 'REPOSITORY_NAME=Sandbox_Hive',
      file => "/tmp/xasecure/xasecure-hive-${xasecure_version}-release/install.properties",
    }

    sed {'hive-XAAUDIT.DB.HOSTNAME':
      line    => '^XAAUDIT.DB.HOSTNAME=$',
      replace => 'XAAUDIT.DB.HOSTNAME=localhost',
      file => "/tmp/xasecure/xasecure-hive-${xasecure_version}-release/install.properties",
    }
    sed {'hive-XAAUDIT.DB.DATABASE_NAME':
      line    => '^XAAUDIT.DB.DATABASE_NAME=$',
      replace => 'XAAUDIT.DB.DATABASE_NAME=xasecure',
      file => "/tmp/xasecure/xasecure-hive-${xasecure_version}-release/install.properties",
    }
    sed {'hive-XAAUDIT.DB.USER_NAME':
      line    => '^XAAUDIT.DB.USER_NAME=$',
      replace => 'XAAUDIT.DB.USER_NAME=xalogger',
      file => "/tmp/xasecure/xasecure-hive-${xasecure_version}-release/install.properties",
    }
    sed {'hive-XAAUDIT.DB.PASSWORD':
      line    => '^XAAUDIT.DB.PASSWORD=$',
      replace => 'XAAUDIT.DB.PASSWORD=hadoop',
      file => "/tmp/xasecure/xasecure-hive-${xasecure_version}-release/install.properties",
    }
  }
  include properties

  exec {"install-hive":
    command => "bash /tmp/xasecure/xasecure-hive-${xasecure_version}-release/install.sh",
    cwd => "/tmp/xasecure/xasecure-hive-${xasecure_version}-release",
    timeout => 0,
    environment => ["JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk.x86_64"],
    require => [Class[properties]]
  }

  sed {'comment HIVE_SERVER2_OPTS':
    line    => '^(HIVE_SERVER2_OPTS="\$\{HIVE_SERVER2_OPTS\} -hiveconf hive.security\.authenticator\.manager.*)$',
    replace => '# \1',
    file => "/var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/HIVE/package/templates/startHiveserver2.sh.j2",
    require => Exec["install-hive"]
  }

  exec {'hive-agent restart ambari':
    command => 'ambari-server stop; sleep 5; ambari-server start',
    require => Sed['comment HIVE_SERVER2_OPTS'],
  }

  exec {'hive-agent restart ambari agent':
    command => 'ambari-agent stop; sleep 5; ambari-agent start',
    require => Exec['hive-agent restart ambari'],
  }
}

class postinstall::xa-hbase {
  require postinstall::prepare-xasecure

  class properties {
    require postinstall::prepare-xasecure
    sed {'hbase-POLICY_MGR_URL':
      line    => '^POLICY_MGR_URL=$',
      replace => 'POLICY_MGR_URL=http:\/\/sandbox.hortonworks.com:6080',
      file => "/tmp/xasecure/xasecure-hbase-${xasecure_version}-release/install.properties",
    }

    sed {'hbase-REPOSITORY_NAME':
      line    => '^REPOSITORY_NAME=$',
      replace => 'REPOSITORY_NAME=Sandbox_HBase',
      file => "/tmp/xasecure/xasecure-hbase-${xasecure_version}-release/install.properties",
    }

    sed {'hbase-XAAUDIT.DB.HOSTNAME':
      line    => '^XAAUDIT.DB.HOSTNAME=$',
      replace => 'XAAUDIT.DB.HOSTNAME=localhost',
      file => "/tmp/xasecure/xasecure-hbase-${xasecure_version}-release/install.properties",
    }
    sed {'hbase-XAAUDIT.DB.DATABASE_NAME':
      line    => '^XAAUDIT.DB.DATABASE_NAME=$',
      replace => 'XAAUDIT.DB.DATABASE_NAME=xasecure',
      file => "/tmp/xasecure/xasecure-hbase-${xasecure_version}-release/install.properties",
    }
    sed {'hbase-XAAUDIT.DB.USER_NAME':
      line    => '^XAAUDIT.DB.USER_NAME=$',
      replace => 'XAAUDIT.DB.USER_NAME=xalogger',
      file => "/tmp/xasecure/xasecure-hbase-${xasecure_version}-release/install.properties",
    }
    sed {'hbase-XAAUDIT.DB.PASSWORD':
      line    => '^XAAUDIT.DB.PASSWORD=$',
      replace => 'XAAUDIT.DB.PASSWORD=hadoop',
      file => "/tmp/xasecure/xasecure-hbase-${xasecure_version}-release/install.properties",
    }
  }
  include properties

  exec {"install-hbase":
    command => "bash /tmp/xasecure/xasecure-hbase-${xasecure_version}-release/install.sh",
    cwd => "/tmp/xasecure/xasecure-hbase-${xasecure_version}-release",
    timeout => 0,
    environment => ["JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk.x86_64"],
    require => [Class[properties]]
  }

  ambariApi {"restart hbase":
    url => "requests",
    method => "POST",
    body => '{"RequestInfo":{"command":"RESTART","context":"Restart all components for HBASE","operation_level":{"level":"SERVICE","cluster_name":"Sandbox","service_name":"HBASE"}},"Requests/resource_filters":[{"service_name":"HBASE","component_name":"HBASE_CLIENT","hosts":"sandbox.hortonworks.com"},{"service_name":"HBASE","component_name":"HBASE_MASTER","hosts":"sandbox.hortonworks.com"},{"service_name":"HBASE","component_name":"HBASE_REGIONSERVER","hosts":"sandbox.hortonworks.com"}]}',
    require => Exec["install-hbase"]
  }
}

class postinstall::xasecure {
  include postinstall::xa-policymgr
  include postinstall::xa-hadoop
  # include postinstall::xa-hive
  # include postinstall::xa-hbase
}
