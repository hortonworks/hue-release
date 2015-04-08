USER=hue

[ ! -f /root/.hdfs_prepared ] && (

echo "Installing udfs"
su - hdfs -c "hdfs dfs -mkdir /tmp/udfs"
su - hdfs -c "hdfs dfs -chmod 777 /tmp/udfs"
su - $USER -c "hdfs dfs -put /usr/hdp/current/hbase-client/lib/guava-*.jar /tmp/udfs/guava.jar"
su - $USER -c "hdfs dfs -put /usr/hdp/current/hbase-client/lib/zookeeper.jar /tmp/udfs/zookeeper.jar"
su - $USER -c "hdfs dfs -put /usr/hdp/current/hbase-client/lib/hbase-common-*.jar /tmp/udfs/"
su - $USER -c "hdfs dfs -put /usr/hdp/current/hbase-client/lib/hbase-client-*.jar /tmp/udfs/"
su - $USER -c "hdfs dfs -put /usr/hdp/current/pig-client/lib/piggybank.jar /tmp/udfs/piggybank.jar"


su - $USER -c "/usr/lib/hue/build/env/bin/hue create_sandbox_user"
su - $USER -c "/usr/lib/hue/build/env/bin/hue install_udfs"
su - $USER -c "/usr/lib/hue/build/env/bin/hue oozie_setup"
su - $USER -c "/usr/lib/hue/build/env/bin/hue jobsub_setup"
su - $USER -c "/usr/lib/hue/build/env/bin/hue beeswax_install_examples"

echo "Adding guest user"
su - hdfs -c "hdfs dfs -mkdir /user/guest"
su - hdfs -c "hdfs dfs -chown guest:guest /user/guest"

echo "Adding yarn user"
su - hdfs -c "hdfs dfs -mkdir /user/yarn"
su - hdfs -c "hdfs dfs -chown yarn:yarn /user/yarn"

touch /root/.hdfs_prepared
/etc/init.d/hue restart
)
exit 0
