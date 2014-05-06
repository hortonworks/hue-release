/etc/init.d/ntpd start
cat /etc/hosts >> /tmp/hosts
yum install -y http://s3.amazonaws.com/dev.hortonworks.com/AMBARI.dev-1.x/repos/centos6/AMBARI.dev-1.x-1.el6.noarch.rpm
yum install -y ambari-agent
sed -i.bak "/^hostname/ s/.*/hostname=ambari.hortonworks.com/" /etc/ambari-agent/conf/ambari-agent.ini
ambari-agent start
/usr/sbin/sshd -D
