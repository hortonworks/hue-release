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

define replace($file, $pattern, $replacement) {
    exec { "/usr/bin/perl -pi -e 's/$pattern/$replacement/' '$file'":
        onlyif => "/usr/bin/perl -ne 'BEGIN { \$ret = 1; } \$ret = 0 if
/$pattern/ && ! /$replacement/ ; END { exit \$ret; }' '$file'",
    }
}



class ldap {
    package {['openldap-servers', 'openldap-clients', 'openldap', 'migrationtools']:
        ensure => present,
    }


    line { rootpw:
        file => "/etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif",
        line => "olcRootPW: 1111",
        require => Package['openldap-servers'],
        notify => Service['slapd'],
    }

    line { managerpw:
        file => "/etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif",
        line => "olcRootPW: 2222",
        require => Package['openldap-servers'],
        notify => Service['slapd'],
    }

    replace { managersuffix:
        file => "/etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif",
        pattern => "olcSuffix: .*",
        replacement => "olcSuffix: dc=sandbox,dc=hortonworks,dc=com",
        require => Package['openldap-servers'],
        notify => Service['slapd'],
    }

    replace { managerdn:
        file => "/etc/openldap/slapd.d/cn=config/olcDatabase={2}bdb.ldif",
        pattern => "olcRootDN: .*",
        replacement => "olcRootDN: cn=Manager,dc=sandbox,dc=hortonworks,dc=com",
        require => Package['openldap-servers'],
        notify => Service['slapd'],
    }

    service {'slapd':
        ensure => running,
        require => Package['openldap-servers'],
    }

    exec {'base':
        command => '/usr/bin/ldapadd -w 2222 -D "cn=Manager,dc=sandbox,dc=hortonworks,dc=com" -f /vagrant/ldif/base.ldif; true'
    }

    exec {'users':
        command => '/usr/bin/ldapadd -w 2222 -D "cn=Manager,dc=sandbox,dc=hortonworks,dc=com" -f /vagrant/ldif/passwd.ldif; true'
    }

    exec {'groups':
        command => '/usr/bin/ldapadd -w 2222 -D "cn=Manager,dc=sandbox,dc=hortonworks,dc=com" -f /vagrant/ldif/group.ldif; true'
    }

    service {'iptables':
        ensure => stopped,
    }

    file {'/etc/sysconfig/network-scripts/ifcfg-eth1':
        ensure => file,
        content => "DEVICE=eth1\nBOOTPROTO=dhcp\nMTU=1500\nNM_CONTROLLED=yes\nONBOOT=yes\nTYPE=Ethernet\n",
    }
}

include ldap
