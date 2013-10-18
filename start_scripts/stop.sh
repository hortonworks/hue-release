#----- Stop script -------------

# host machine
echo "Stop Oozie"
su -l oozie -c "cd /var/log/oozie; /usr/lib/oozie/bin/oozied.sh stop"

# host machine
echo "Stop WebHCat"
su -l hcat -c "/usr/lib/hcatalog/sbin/webhcat_server.sh stop"

# host machine
echo "Stop Tez"
su -l tez -c "/usr/lib/tez/sbin/tez-daemon.sh stop ampoolservice"

# host machine
echo "Stop Hive"
ps aux | awk '{print $1,$2}' | grep hive | awk '{print $2}' | xargs kill >/dev/null 2>&1

# host machine
echo "Stop ZooKeeper"
su -l zookeeper -c "export ZOOCFGDIR=/etc/zookeeper/conf ; export ZOOCFG=zoo.cfg ;source /etc/zookeeper/conf/zookeeper-env.sh ; /usr/lib/zookeeper/bin/zkServer.sh stop"

echo "Stop HBase"
# slave node
echo "Stop Hbase RegionServers"
su -l hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf stop regionserver"

# master node
echo "Stop Hbase Master"
su -l hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf stop master"

echo "Stop Hbase Stargate"
su -l hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh stop rest"

echo "Stop Hbase thrift"
su -l hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh stop thrift"

echo "Stop YARN"
# slave node
echo "Stop NodeManagers"
su -l yarn -c "export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf stop nodemanager"

# host machine
echo "Stop JobTracker History Server"
su -l mapred -c "export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf stop historyserver"

# host machine
echo "Stop ResourceManager"
su -l yarn -c "export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf stop resourcemanager"

echo "Stop HDFS"
# slave node
echo "Stop DataNodes"
su -l hdfs -c "/usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf stop datanode"

# host machine
echo "Stop Secondary NameNode"
su -l hdfs -c "/usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf stop secondarynamenode"

# master node
echo "Stop NameNode"
su -l hdfs -c "/usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf stop namenode"

echo "Stop MySQL server"
/etc/init.d/mysqld stop
/etc/init.d/postgresql stop

echo "Service associated with port"
netstat -nltp

echo
echo
echo "Java Process"
ps auxwwwf | grep java | grep -v grep | awk '{print $1, $11,$12}'

echo

