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
        content => template("/vagrant/sandbox.repo"),
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

    package { 'sandbox':
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
        content => template("/vagrant/splash/start-ttys.conf"),
    }

    file { 'tty1':
        path    => "/etc/init/tty-splash.conf",
        content => template("/vagrant/splash/tty-splash.conf"),
    }

    file { 'bashrc':
        path    => "/root/.bashrc",
        content => template("/vagrant/splash/bashrc"),
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
        require => Class["splash_opts"],
    }
}


class tutorials {
    include sandbox_rpm

    service { "httpd":
        ensure => running,
        require => Class[sandbox_rpm],
    }
}


class sandbox {

    include sandbox_rpm
    include tutorials

    file { 'startHiveserver2.sh':
        path    => "/tmp/startHiveserver2.sh",
        content => template("/vagrant/scripts/startHiveserver2.sh"),
    }

    file { 'startMetastore.sh':
        path    => "/tmp/startMetastore.sh",
        content => template("/vagrant/scripts/startMetastore.sh"),
    }

    exec { 'start':
        command => "/etc/init.d/startup_script start",
        require => [ File["startHiveserver2.sh"], 
                     File["startMetastore.sh"],
                     Class[sandbox_rpm],
                    ],
    }

    service { "supervisord":
        ensure => running,
        require => [ Class[tutorials],
                     Exec[start] ],
    }
}


class java_home {

file { "/etc/bashrc": ensure => present, }

line { java_home:
    file => "/etc/bashrc",
    line => "export JAVA_HOME=/usr/jdk/jdk1.6.0_31/",
}

}



include splash
include sandbox
