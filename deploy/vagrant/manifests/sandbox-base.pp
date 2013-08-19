
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
        require => [Package['yum-plugin-priorities']],
    }

    file { 'issue':
        path    => "/etc/issue",
        content => template("/vagrant/files/issue"),
        ensure  => file,
    }

    exec { 'issue-credentials':
        command => "initctl restart tty TTY=/dev/tty5; initctl restart tty TTY=/dev/tty2; true",
        require => File[issue],
    }

    package { "libxslt":
        ensure => present,
        require => File['resolv.conf'],
    }

    package { "python-lxml":
        ensure => present,
        require => File['resolv.conf'],
    }

    package { "wget":
      ensure => present,
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
                     Package['yum-plugin-priorities']
                     
                   ],
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

class groups_fix {
      file { 'groups_fix.sh':
        path    => "/tmp/groups_fix.sh",
        content => template("/vagrant/files/scripts/groups_fix.sh"),
      }

      exec { "groups_fix.sh":
        command => '/bin/bash /tmp/groups_fix.sh |tee /var/log/groups_fix.log',
        require => File['groups_fix.sh'],
        timeout => 0,
        logoutput=> "on_failure",
      }
}

class java_home {
    file { "/etc/bashrc": ensure => present, }

    line { java_home:
        file => "/etc/bashrc",
        line => "export JAVA_HOME=/usr/jdk/jdk1.6.0_31/",
    }
}

class sandbox {
    include sandbox_rpm
    include hdfs_prepare
    include groups_fix
    include java_home



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

    exec { 'start':
        command => "/etc/init.d/startup_script restart",
        require => [   Class[sandbox_rpm],
                       Class[groups_fix],
                    ],
    }

}


include sandbox
