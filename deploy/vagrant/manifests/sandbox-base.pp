
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

    package { "knox":
      ensure => present,
    }

    package { ['hue', 'hue-sandbox']:
        ensure => latest,
        require => [ File['sandbox.repo'],
                     Package['libxslt'],
                     Package['python-lxml'],
                     Package['yum-plugin-priorities']
                     
                   ],
    }

    file { "/etc/hue/conf/hue.ini":
       path => "/etc/hue/conf/hue.ini",
       content => template("/vagrant/files/hue.ini"),
       require => Package['hue']
    }

    exec { 'hue_password':
       command => "echo 'hue:hadoop' | chpasswd",
       require => Package['hue'],
    }

    exec { 'hue_sudoers':
       command => "echo -e 'hue ALL=(ALL) ALL\nhue ALL=(ALL) NOPASSWD: /sbin/chkconfig\nhue ALL=(ALL) NOPASSWD: /sbin/service\nhue ALL=(ALL) NOPASSWD: /bin/kill' >> /etc/sudoers",
       require => Package['hue'],
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

class custom_fixes {
      file { 'custom_fixes.sh':
        path    => "/tmp/custom_fixes.sh",
        content => template("/vagrant/files/scripts/custom_fixes.sh"),
      }

      exec { "custom_fixes.sh":
        command => '/bin/bash /tmp/custom_fixes.sh |tee /var/log/custom_fixes.log',
        require => File['custom_fixes.sh'],
        timeout => 0,
        logoutput=> "on_failure",
      }

      exec {'ambari-url-fix.sh':
        command => '/bin/bash /vagrant/files/scripts/ambari-url-fix.sh',
        timeout => 0,
        logoutput=> "on_failure",
      }
}

class java_home {
  file {'java.sh':
    path => '/etc/profile.d/java.sh',
    content => template("/vagrant/files/scripts/java.sh"),    
  }
}

class sandbox {
    include sandbox_rpm
    include hdfs_prepare
    include custom_fixes
    include java_home

    file { 'vmware-tools.sh':
        path    => "/usr/libexec/vmware-tools.sh",
        content => template("/vagrant/files/scripts/vmware-tools.sh"),
    }

/*    file {"/usr/lib/hue/apps/shell/src/shell/build/setuid":
        ensure => file,
        mode => 4755,
        require => Class[sandbox_rpm],
      }
*/
    service { 'iptables':
        ensure => stopped,
        enable => false,
    }

    exec { 'iptables -F':
        onlyif => "which iptables",
        require => Service['iptables']
    }

    line { no_priority:
        ensure => absent,
        file => "/etc/yum.repos.d/sandbox.repo",
        line => "priority=1",
        require => Class[sandbox_rpm]
    }

    service { 'hadoop-yarn-resourcemanager':
        ensure => stopped,
        enable => false,
    }

    service { 'hadoop-yarn-nodemanager':
        ensure => stopped,
        enable => false,
    }

    service { 'hadoop-mapreduce-historyserver':
        ensure => stopped,
        enable => false,
    }

    exec { 'start':
        command => "/etc/init.d/startup_script restart",
        require => [   Class[sandbox_rpm],
                       Class[custom_fixes],
                       Service['hadoop-yarn-resourcemanager'],
                       Service['hadoop-yarn-nodemanager'],
                       Service['hadoop-mapreduce-historyserver'],
                    ],
    }

    replace { "/etc/sysconfig/network":
       file => "/etc/sysconfig/network",
       pattern => "HOSTNAME=sandbox",
       replacement => "HOSTNAME=sandbox.hortonworks.com",
    }

    exec { 'hostname':
        command => "hostname sandbox.hortonworks.com",
    }

    user { 'guest':
        name => 'guest',
        ensure => present,
        groups => ["users"],
        home => '/home/guest',
        managehome => true,
    }
}

class optimizations {
    # Virtual memory optimizations
    file { 'memory_clean':
        path    => "/etc/cron.d/99memory_clean",
        content => template("/vagrant/files/memory_clean_cron"),
        ensure  => file,
    }

    line { dirty_ratio:
        ensure => present,
        file => "/etc/sysctl.conf",
        line => "vm.dirty_background_ratio = 1",
    }

    line { dirty_background_ratio:
        ensure => present,
        file => "/etc/sysctl.conf",
        line => "vm.dirty_ratio = 5",
    }

    file { 'zram_init.sh':
        path    => "/usr/libexec/zram_init.sh",
        content => template("/vagrant/files/scripts/zram_init.sh"),
    }

    exec { "zram_init.sh":
        command => '/bin/bash /usr/libexec/zram_init.sh',
        require => [File['zram_init.sh']],
        timeout => 0,
        logoutput=> "on_failure",
    }

    line { zram_rc_local:
        ensure => present,
        file => "/etc/rc.local",
        line => "bash /usr/libexec/zram_init.sh",
    }

    # Unnecessary services
    exec { 'ip6tables -F':
        onlyif => "which ip6tables",
        require => Service['ip6tables']
    }

    service { 'ip6tables':
        ensure => stopped,
        enable => false,
    }

    service { 'cups':
        ensure => stopped,
        enable => false,
    }

    service { 'iscsi':
        ensure => stopped,
        enable => false,
    }

    service { 'iscsid':
        ensure => stopped,
        enable => false,
    }

    service { 'mdmonitor':
        ensure => stopped,
        enable => false,
    }

    service { 'auditd':
        ensure => stopped,
        enable => false,
    }

    file { '/etc/cron.daily/readahead.cron':
        ensure => absent,
    }

    file { '/lib/udev/rules.d/75-persistent-net-generator.rules':
        ensure => absent,
    }

    file { '/etc/udev/rules.d/70-persistent-net.rules':
        ensure => absent,
    }

    file { '/etc/cron.monthly/readahead-monthly.cron':
        ensure => absent,
    }
}

include sandbox
include optimizations
