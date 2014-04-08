cd /tmp/;
curl -H "X-Requested-By: ambari" -u admin:admin http://127.0.0.1:8080/api/v1/blueprints/single-node-sandbox -d @bluprint-1-node.json
curl -H "X-Requested-By: ambari" -u admin:admin http://127.0.0.1:8080/api/v1/clusters/Sandbox2 -d @- <<EOF
{
  "blueprint" : "single-node-sandbox2",
  "host-groups" :[
    {
      "name" : "host_group_1",
      "hosts" : [
        {
          "fqdn" : "sandbox.hortonworks.com"
        }
      ]
    }
  ]
}
EOF


## check status
curl -s -u admin:admin -H "X-Requested-By: ambari" 'http://127.0.0.1:8080/api/v1/clusters/Sandbox/requests/1?fields=tasks/Tasks/*'
