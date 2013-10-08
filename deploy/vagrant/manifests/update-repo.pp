file { 'HDP.repo':
    path    => "/etc/yum.repos.d/HDP.repo",
    ensure  => absent,
}

exec { 'yum_clean_all':
    command => "/usr/bin/yum clean all",
    require => [File['HDP.repo']]
}

file { 'ambari.repo':
    path    => "/etc/yum.repos.d/ambari.repo",
    content => template("/vagrant/files/ambari.repo"),
    ensure  => file,
    require => [Exec['yum_clean_all']],
}