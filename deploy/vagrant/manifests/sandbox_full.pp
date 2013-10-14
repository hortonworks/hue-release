import "sandbox-base.pp"

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

    package { 'epel-release':
        ensure => present,
    }

    package { 'python-pip':
        ensure => present,
        require => Package["epel-release"],
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

    package {'hue-tutorials':
        ensure => latest,
        require => Class['sandbox_rpm'],
    }

/*  Disable showing Sandbox build hash for release */
/*    file {'/var/lib/hue/EXTRA_VERSIONS':
        ensure => absent,
        require => Package['hue-tutorials'],
    }
*/
/*  Disable single user mode
    file {'/var/lib/hue/single_user_mode':
        ensure => absent,
        require => Package['hue-tutorials'],
    }
*/

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

class sandbox_customize inherits sandbox {
    include tutorials
    include optimizations

    service { "hue":
        ensure => running,
        require => [ Class[sandbox_rpm],
                     Exec[start] ],
    }

    service { "tutorials":
        ensure => running,
        require => [ Class[sandbox_rpm],
                     Package['hue-tutorials'],
                     Exec[start] ],
    }

    file {'/root/start_ambari.sh':
        ensure => link,
        target => "/usr/lib/hue/tools/start_scripts/start_ambari.sh",
        mode => 0755,
    }

    file {'/root/start_hbase.sh':
        ensure => link,
        target => "/usr/lib/hue/tools/start_scripts/start_hbase.sh",
        mode => 0755,
    }

    package { 'acpid':
        ensure => installed,
    }

    package { 'mlocate':
        ensure => installed,
    }

    exec { 'updatedb':
        command => "updatedb",
        require => Package["mlocate"],
    }
}


include splash
include sandbox_customize
