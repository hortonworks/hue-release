Exec { path => [ "/bin/", "/sbin/", "/usr/bin/", "/usr/sbin/", "/usr/local/bin" ] }

stage { 'prepare': }
stage { 'install': }
stage { 'postinstall': }

Stage['prepare'] -> Stage['install'] -> Stage['postinstall']


node default {
  class {prepare:
    stage => prepare
  }
  class {install:
    stage => install
  }
  class {postinstall:
    stage => postinstall
  }
}

node /^host[0-9]\.hortonworks\.com$/ {
  include prepare
  include install::ambari-agent
  include install::finish-cluster
  include postinstall::accumulo
}
