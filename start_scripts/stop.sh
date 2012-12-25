#----- Stop script -------------
echo "For slave node(s)"

echo "Stop Hbase regionserver"
su - hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf stop regionserver"

echo "Stop HDFS datanode"
su - hdfs -c "/usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf stop datanode"

echo "Stop Hadoop tasktracker"
su - mapred -c "/usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf stop tasktracker"

echo "Stop templeton server"
su - hcat -c '/usr/lib/hcatalog/sbin/webhcat_server.sh stop'

echo "Stop Oozie"
su - oozie -c "cd /var/log/oozie; /usr/lib/oozie/bin/oozie-stop.sh"

echo "For ZooKeeper node(s)"
echo "Stop zookeeper node"
su - zookeeper -c  'source /etc/zookeeper/conf/zookeeper-env.sh ; /bin/env ZOOCFGDIR=/etc/zookeeper/conf ZOOCFG=zoo.cfg /usr/lib/zookeeper/bin/zkServer.sh stop'

echo "For Master node(s)"
echo "Stop the hbase master"
su - hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf stop master"

echo "Stop the job tracker and history server"
su - mapred -c "/usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf stop historyserver"
su - mapred -c "/usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf stop jobtracker"

echo "Stop the secondary name node"
su - hdfs -c "/usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf stop secondarynamenode"

echo "Stop the name node"
su - hdfs -c "/usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf stop namenode"

echo "Stop the hcat server"
kill -9 `ps -ef | grep hive | grep hadoop | awk '{ print $2 }'`

echo "Stop MySQL server"
/etc/init.d/mysqld stop
/etc/init.d/postgresql stop

echo "Service associated with port"
netstat -nltp

echo "     			"
echo "                          "
echo "Java Process"
ps auxwwwf | grep java | grep -v grep | awk '{print $1, $11,$12}'

echo "======================================="

