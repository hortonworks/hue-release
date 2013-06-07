
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
            exec { "/bin/grep -vFx '${line}' '${file}' | /usr/bin/tee '${file}.new' > /dev/null 2>&1; mv -f '${file}.new' '${file}' > /dev/null 2>&1":
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

define replace($file, $pattern, $replacement) {
    exec { "/usr/bin/perl -pi -e 's/$pattern/$replacement/' '$file'":
        onlyif => "/usr/bin/perl -ne 'BEGIN { \$ret = 1; } \$ret = 0 if
/$pattern/ && ! /$replacement/ ; END { exit \$ret; }' '$file'",
    }
}


class sandbox_rpm {
    replace { "/etc/hive/conf/hive-site.xml":
       file => "/etc/hive/conf/hive-site.xml",
       pattern => "jdbc:mysql:\\/\\/sandbox.hortonworks.com",
       replacement => "jdbc:mysql:\\/\\/localhost:3306"
    }

    file { '/etc/sysconfig/network-scripts/ifcfg-eth1':
        ensure => absent,
    }

    file { '/virtualization':
        content => "vbox",
    }

    file { 'resolv.conf':
        path    => "/etc/resolv.conf",
        content => "nameserver 8.8.8.8",
    }

    package { "yum-plugin-priorities":
        ensure => present,
    }

    file { 'sandbox.repo':
        path    => "/etc/yum.repos.d/sandbox.repo",
        content => template("/vagrant/files/sandbox.repo"),
        ensure  => file,
        require => Package['yum-plugin-priorities'],
    }

    package { "libxslt":
        ensure => present,
        require => File['resolv.conf'],
    }

    package { "python-lxml":
        ensure => present,
        require => File['resolv.conf'],
    }

    exec { 'yum-cache':
        command => "yum clean all --disablerepo='*' --enablerepo='sandbox' --enablerepo='hue-bigtop'",
    }

    package { ['hue', 'hue-sandbox', 'hue-plugins']:
        ensure => latest,
        require => [ File['sandbox.repo'],
                     Package['libxslt'],
                     Package['python-lxml'],
                     Exec['yum-cache'],
                     Package['yum-plugin-priorities'],
                     User['hue'],
                   ],
    }

    package {'hue-tutorials':
        ensure => latest,
        require => Package['hue-sandbox'],
    }

/*  Disable single user mode
    file {'/var/lib/hue/single_user_mode':
        ensure => absent,
        require => Package['hue-tutorials'],
    }
*/

    user { "hue":
      ensure     => "present",
      managehome => true,
      home => "/usr/lib/hue",
      uid => "505",
      gid => "hadoop",
      groups => ["admin", "users"],
      password => '$1$MwHL5JF5$1WmQPYETuWUyhCKLEyN9a1',
    }

    group { "hadoop":
        ensure => "present",
    }

    group { "users":
        ensure => "present",
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
        command => "initctl stop tty TTY=/dev/tty1; initctl start tty-splash TTY=/dev/tty1; true",
        require => [Class["splash_opts"],
                    Class["sandbox"] ],
    }
}


class tutorials {
    include sandbox_rpm

    package { "wget":
      ensure => present,
    }
      

    file { 'load_videos.sh':
      path    => "/tmp/load_videos.sh",
      content => template("/vagrant/files/scripts/load_videos.sh"),
    }

    exec { "load_videos.sh":
      command => '/bin/bash /tmp/load_videos.sh | tee /var/log/load_videos.log',
      require => [File['load_videos.sh']],
      timeout => 0,
      logoutput => "on_failure",
    }

    service { "httpd":
        ensure => running,
        require => [ Class[sandbox_rpm], ],
    }

    file { 'apache-hue.conf':
        path    => "/etc/httpd/conf.d/hue.conf",
        content => template("/vagrant/files/apache-hue.conf"),
        ensure  => file,
        notify  => Service['httpd'],
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
            

      file { 'hdfs_prepare.sh':
        path    => "/tmp/hdfs_prepare.sh",
        content => template("/vagrant/files/scripts/hdfs_prepare.sh"),
      }

      exec { "hdfs_prepare.sh":
        command => '/bin/bash /tmp/hdfs_prepare.sh |tee /var/log/hdfs_start.log',
        require => [File['hdfs_prepare.sh'], Exec["start"], Package["wget"]],
        timeout => 0,
        logoutput=> "on_failure",
      }
}

class sandbox {
    include java_home
    include sandbox_rpm
    include tutorials
    include hdfs_prepare

    file {"/usr/lib/hive/lib/hcatalog-core.jar":
        ensure => link,
        target => "/usr/lib/hcatalog/share/hcatalog/hcatalog-core.jar",
        mode => 0755,
      }


    
    exec { 'start':
        command => "/etc/init.d/startup_script restart",
      require => [   File["/usr/lib/hive/lib/hcatalog-core.jar"],
                     Class[sandbox_rpm],
                    ],
    }

    service { "hue":
        ensure => running,
        require => [ Class[sandbox_rpm],
                     Exec[start] ],
    }

    service { "tutorials":
        ensure => running,
        require => [ Class[sandbox_rpm],
                     Exec[start] ],
    }

    file {'/root/start_ambari.sh':
        ensure => link,
        target => "/usr/lib/hue/tools/start_scripts/start_ambari.sh",
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

    line { no_priority:
        ensure => absent,
        file => "/etc/yum.repos.d/sandbox.repo",
        line => "priority=1",
        require => Class[sandbox_rpm]
    }
}



include splash
include sandbox
