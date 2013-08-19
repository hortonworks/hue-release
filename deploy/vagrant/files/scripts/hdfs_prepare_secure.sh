/sbin/service krb5kdc start
/sbin/service kadmin start
kinit -kt /etc/security/hdfs.headless.keytab hdfs
rm /usr/lib/hcatalog/share/webhcat/svr/webhcat*.jar
su - root -c "/usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf start datanode"
