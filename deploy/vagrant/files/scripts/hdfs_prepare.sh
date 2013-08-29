USER=hue

[ ! -f /root/.hdfs_prepared ] && (

echo "Installing udfs"
su - hdfs -c "hadoop dfs -mkdir /tmp/udfs"
su - hdfs -c "hadoop dfs -chmod 777 /tmp/udfs"
su - $USER -c "hadoop dfs -put /usr/lib/hbase/lib/guava-*.jar /tmp/udfs/guava.jar"
su - $USER -c "hadoop dfs -put /usr/lib/hbase/lib/zookeeper.jar /tmp/udfs/zookeeper.jar"
su - $USER -c "hadoop dfs -put /usr/lib/hbase/lib/hbase-common-*.jar /tmp/udfs/"
su - $USER -c "hadoop dfs -put /usr/lib/hbase/lib/hbase-client-*.jar /tmp/udfs/"
su - $USER -c "hadoop dfs -put /usr/lib/pig/piggybank.jar /tmp/udfs/piggybank.jar"

cd /tmp
tar xvf udfs.tar.gz
chown $USER udfs
usermod -a -G users $USER
su - $USER -c "hadoop fs -copyFromLocal /tmp/udfs /tmp/udfs"
su - $USER -c "hadoop fs -chmod -R 777 /tmp/udfs"
su - $USER -c "/usr/lib/hue/build/env/bin/hue create_sandbox_user"
su - $USER -c "/usr/lib/hue/build/env/bin/hue install_udfs"
su - $USER -c "/usr/lib/hue/build/env/bin/hue oozie_setup"
su - $USER -c "/usr/lib/hue/build/env/bin/hue jobsub_setup"
su - $USER -c "/usr/lib/hue/build/env/bin/hue beeswax_install_examples"
rm /tmp/udfs.tar.gz
rm  -rf /tmp/udfs
touch /root/.hdfs_prepared
/etc/init.d/hue restart
)
exit 0
