Exec { path => [ "/bin/", "/sbin/", "/usr/bin/", "/usr/sbin/", "/usr/local/bin" ] }

stage { 'prepare': }
stage { 'install': }
stage { 'postinstall': }
stage { 'postinstall_1': }
stage { 'postinstall_2': }
stage { 'postinstall_3': }

Stage['prepare'] -> Stage['install'] -> Stage['postinstall'] -> Stage['postinstall_1'] -> Stage['postinstall_2'] -> Stage['postinstall_3']


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

define ambariApi($url, $body, $method = 'POST') {
  case $method {
    POST: {
      exec {"/usr/bin/curl  -H \"X-Requested-By: ambari\"  -u admin:admin -d '${body}' http://127.0.0.1:8080/api/v1/clusters/Sandbox/${url} | python /tmp/wait_finish.py; sleep 5":
        logoutput => true,
        timeout => 600,
      }
    }
    PUT: {
      exec {"/usr/bin/curl  -H \"X-Requested-By: ambari\"  -u admin:admin -X PUT -d '${body}' http://127.0.0.1:8080/api/v1/clusters/Sandbox/${url} | python /tmp/wait_finish.py; sleep 5":
        logoutput => true,
      }
    }
  }
}
