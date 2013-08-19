#HOME="/home/hadoop"
#HOME1="/home"
line="50"

#------- Start script ---------
echo "Starting Postgresql"
/etc/init.d/postgresql start;sleep 5

echo "Start name node"
su - hdfs -c  "export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf start namenode";sleep 5
tail -$line  /var/log/hadoop/hdfs/hadoop-hdfs-namenode-*.log

echo "Start data node"
su - hdfs -c  "export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf start datanode";sleep 5
tail -$line  /var/log/hadoop/hdfs/hadoop-hdfs-datanode-*.log

echo "Start secondary name node"
su - hdfs -c  "export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf start secondarynamenode";sleep 5
tail -$line  /var/log/hadoop/hdfs/hadoop-hdfs-secondarynamenode-*.log

echo "Start history server"
su - mapred -c  'export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop-mapreduce/sbin/mr-jobhistory-daemon.sh --config /etc/hadoop/conf start historyserver'
tail -$line  /var/log/hadoop-mapreduce/mapred/mapred-mapred-historyserver-sandbox.out

echo "Start zookeeper nodes"
su - zookeeper -c  'source /etc/zookeeper/conf/zookeeper-env.sh ; /bin/env ZOOCFGDIR=/etc/zookeeper/conf ZOOCFG=zoo.cfg /usr/lib/zookeeper/bin/zkServer.sh start'

echo "Start hbase master"
su - hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf start master; sleep 25"
tail -$line  /var/log/hbase/hbase-hbase-master-*.log

echo "Start hbase regionservers"
su - hbase -c "/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf start regionserver";sleep 5
tail -$line  /var/log/hbase/hbase-hbase-regionserver-*.log

echo "Start Hiveserver2"
/etc/init.d/mysqld start
#su - hive -c  'env HADOOP_HOME=/usr nohup hive --service hiveserver2 > /var/log/hive/hive.out 2> /var/log/hive/hive.log & '
su - hive -c  'env JAVA_HOME=/usr/jdk/jdk1.6.0_31 /tmp/startHiveserver2.sh /var/log/hive/hive-server2.out  /var/log/hive/hive-server2.log /var/run/hive/hive-server.pid /etc/hive/conf.server '
tail -$line  /var/log/hive/hive.log

echo "Start hcat server"
su - hive -c  'env HADOOP_HOME=/usr JAVA_HOME=/usr/jdk/jdk1.6.0_31 /tmp/startMetastore.sh /var/log/hive/hive.out /var/log/hive/hive.log /var/run/hive/hive.pid /etc/hive/conf.server '
tail -$line  /var/log/hive/hive.log


echo "Start templeton server"
su - hcat -c '/usr/lib/hcatalog/sbin/webhcat_server.sh start'
tail -$line  /var/log/webhcat/webhcat.log

echo "Start Oozie"
su - oozie -c "cd /var/log/oozie; /usr/lib/oozie/bin/oozie-start.sh"
tail -$line  /var/log/oozie/oozie.log


# YARN
su - yarn -c  'export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop-yarn/sbin/yarn-daemon.sh --config /etc/hadoop/conf start resourcemanager'
su - yarn -c  'export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop-yarn/sbin/yarn-daemon.sh --config /etc/hadoop/conf start resourcemanager'
su - mapred -c  'export HADOOP_LIBEXEC_DIR=/usr/lib/hadoop/libexec && /usr/lib/hadoop-mapreduce/sbin/mr-jobhistory-daemon.sh --config /etc/hadoop/conf start historyserver'



# echo "Starting Ganglia"
# /etc/init.d/gmetad stop
# /etc/init.d/gmond stop
# /etc/init.d/hdp-gmetad start
# /etc/init.d/hdp-gmond start


# echo "starting Nagios"
# /etc/init.d/nagios start;sleep 5

# echo "Starting Ambari server"
# ambari-server start; sleep 5

# echo "Starting Ambari agent"
# ambari-agent start

echo "Service associated with port"
netstat -nltp

echo "*********************************************"

echo "Java Process"
ps auxwwwf | grep java | grep -v grep | awk '{print $1, $11,$12}'

