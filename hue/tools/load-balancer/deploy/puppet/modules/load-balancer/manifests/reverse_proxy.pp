import "config.pp"

$CERT_DIR="/etc/ssl"
$PEM_CERT="${CERT_DIR}/haproxy.pem"

class haproxy () {

    include load-balancer::config

    user {"haproxy":
        ensure     => present,
    }

    package { "openssl":
        ensure => latest,
    }

    file { "gen_ssl_cert.sh":
        path => "/tmp/gen_ssl_cert.sh",
        source => "puppet:///modules/load-balancer/gen_ssl_cert.sh",
        require => [Package["openssl"]],
    }

    file {"/etc/haproxy/haproxy.cfg":
        ensure  => file,
        owner => "haproxy",
        content => template("load-balancer/haproxy.cfg.erb"),
        require => [User["haproxy"]],
        notify  => [Service["haproxy"]],
    }

    exec { "/usr/bin/curl -O http://dev2.hortonworks.com.s3.amazonaws.com/hue/thirdparties/haproxy-1.5-1.x86_64.rpm":
        alias => "haproxy_rpm",
        cwd => "/tmp",
    }

    exec { "install_haproxy":
        command => "/bin/bash -c 'rpm -ivh /tmp/haproxy-1.5-1.x86_64.rpm'",
        require => [Exec["haproxy_rpm"]],
        returns => [0, 1],
    }

    service {"haproxy":
        ensure => running,
        enable => true,
        require => [Exec["install_haproxy"]],
    }
}

include haproxy