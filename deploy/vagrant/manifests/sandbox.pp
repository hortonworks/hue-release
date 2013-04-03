$HUE_HOME="/usr/lib/hue"

Exec { path => [ "/bin/", "/sbin/", "/usr/bin/", "/usr/sbin/" ] }

define line($file, $line, $ensure = 'present') {
    case $ensure {
        default : { err ( "unknown ensure value ${ensure}" ) }
        present: {
            exec { "/bin/echo '${line}' >> '${file}'":
                unless => "/bin/grep -qFx '${line}' '${file}'"
            }
        }
        absent: {
            exec { "/bin/grep -vFx '${line}' '${file}' | /usr/bin/tee '${file}' > /dev/null 2>&1":
              onlyif => "/bin/grep -qFx '${line}' '${file}'"
            }

            # Use this resource instead if your platform's grep doesn't support -vFx;
            # note that this command has been known to have problems with lines containing quotes.
            # exec { "/usr/bin/perl -ni -e 'print unless /^\\Q${line}\\E\$/' '${file}'":
            #     onlyif => "/bin/grep -qFx '${line}' '${file}'"
            # }
        }
    }
}


class sandbox_rpm {
    file { 'resolv.conf':
        path    => "/etc/resolv.conf",
        content => "nameserver 8.8.8.8",
    }

    file { 'sandbox.repo':
        path    => "/etc/yum.repos.d/sandbox.repo",
        content => template("/vagrant/files/sandbox.repo"),
        ensure  => file,
    }

    package { "libxslt":
        ensure => present,
        require => File['resolv.conf'],
    }

    package { "python-lxml":
        ensure => present,
        require => File['resolv.conf'],
    }

    package { 'hue-tutorials':
        ensure => present,
        require => [ File['sandbox.repo'],
                     Package['libxslt'],
                     Package['python-lxml'],
                   ]
    }
}


class splash_opts {
    file { 'ttys':
        path    => "/etc/init/start-ttys.conf",
        content => template("/vagrant/files/splash/start-ttys.conf"),
    }

    file { 'tty1':
        path    => "/etc/init/tty-splash.conf",
        content => template("/vagrant/files/splash/tty-splash.conf"),
    }

    file { 'bashrc':
        path    => "/root/.bashrc",
        content => template("/vagrant/files/splash/bashrc"),
    }

    package { 'python-pip':
        ensure => present,
    }

    exec { 'python-sh':
        command => "pip-python install sh",
        require => Package["python-pip"],
        cwd     => "/root",
    }
}


class splash {
    include splash_opts

    exec { 'splash':
        command => "initctl stop tty TTY=/dev/tty1; initctl start tty-splash TTY=/dev/tty1",
        require => [Class["splash_opts"],
                    Class["sandbox"] ],
    }
}


class tutorials {
    include sandbox_rpm

    service { "httpd":
        ensure => running,
        require => [ Class[sandbox_rpm], ],
    }
}

class java_home {
    file { "/etc/bashrc": ensure => present, }

    line { java_home:
        file => "/etc/bashrc",
        line => "export JAVA_HOME=/usr/jdk/jdk1.6.0_31/",
    }
}


class hdfs_prepare {
      package { "wget":
        ensure => present,
      }

      file {'/usr/lib/hcatalog/share/hcatalog/hcatalog-core.jar':
        ensure => link,
        target => "/usr/lib/hive/lib/hcatalog-core.jar",
        mode => 0755,
    }

      file { 'hdfs_prepare.sh':
        path    => "/tmp/hdfs_prepare.sh",
        content => template("/vagrant/files/scripts/hdfs_prepare.sh"),
      }

      exec { "hdfs_prepare.sh":
        command => '/bin/bash /tmp/hdfs_prepare.sh > /var/log/hdfs_start.log',
        require => [File['hdfs_prepare.sh'], Exec["start"]],
        timeout => 0
      }
}

class sandbox {
    include java_home
    include sandbox_rpm
    include tutorials
    include hdfs_prepare

    file { 'startHiveserver2.sh':
        path    => "/tmp/startHiveserver2.sh",
        content => template("/vagrant/files/scripts/startHiveserver2.sh"),
        owner   => hive,
        mode   => 755,
    }

    file { 'startMetastore.sh':
        path    => "/tmp/startMetastore.sh",
        content => template("/vagrant/files/scripts/startMetastore.sh"),
        owner   => hive,
        mode  => 755,
    }

    file { 'hue-plugins-2.2.0-SNAPSHOT.jar':
        path    => "/usr/lib/hadoop/lib/hue-plugins-2.2.0-SNAPSHOT.jar",
        content => file("/vagrant/files/jars/hue-plugins-2.2.0-SNAPSHOT.jar"),
    }

    file {"${HUE_HOME}/apps/shell/src/shell/build/setuid":
        owner => sandbox,
        group => sandbox,
        mode => 4750,
        require => [Class[sandbox_rpm]],
    }

    exec { 'start':
        command => "/etc/init.d/startup_script start",
        require => [ File["startHiveserver2.sh"],
                     File["startMetastore.sh"],
                     File["hue-plugins-2.2.0-SNAPSHOT.jar"],
                     Class[sandbox_rpm],
                    ],
    }

    service { "supervisord":
        ensure => running,
        require => [ Class[tutorials],
                     Exec[start] ],
    }

    service { "hue":
        ensure => running,
        require => [ Class[sandbox_rpm],
                     Exec[start] ],
    }

    file {'/root/start_ambari.sh':
        ensure => link,
        target => "/usr/lib/start_scripts/start_ambari.sh",
        mode => 0755,
    }

    package { 'acpid':
        ensure => installed,
    }

    service { 'iptables':
        ensure => stopped,
        enable => false,
    }

    exec { 'iptables -F':
        onlyif => "which iptables",
        require => Service['iptables']
    }

    service { 'ip6tables':
        ensure => stopped,
        enable => false,
    }

    exec { 'ip6tables -F':
        onlyif => "which ip6tables",
        require => Service['ip6tables']
    }
}






include splash
include sandbox
