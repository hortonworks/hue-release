[ ! -f /root/.hdfs_prepared ] && (
su - hdfs -c "hadoop fs -rmr -skipTrash /user/ambari_qa/.staging/"
su - hdfs -c "hadoop fs -rm -skipTrash /apps/webhcat/pig.tar.gz"
wget -O /tmp/webhcat.tar.gz http://dev2.hortonworks.com.s3.amazonaws.com/hdfs/webhcat/webhcat.tar.gz
tar xvf /tmp/webhcat.tar.gz -C /tmp
su - hcat -c "hadoop fs -put /tmp/pig.tar.gz /apps/webhcat/pig.tar.gz"
su - hcat -c "hadoop fs -put /tmp/hive.tar.gz /apps/webhcat/hive.tar.gz"
su - hcat -c "hadoop fs -put /tmp/hadoop-streaming.jar /apps/webhcat/hadoop-streaming.jar"
su - hcat -c "hadoop fs -chmod -R 755 /apps/webhcat"
rm -f /tmp/webhcat.tar.gz
echo "Installing udfs"
wget -O /tmp/udfs.tar.gz http://dev2.hortonworks.com.s3.amazonaws.com/hdfs/pig/udfs.tar.gz
cd /tmp
tar xvf udfs.tar.gz
chown sandbox udfs
usermod -a -G users sandbox
su - sandbox -c "hadoop fs -copyFromLocal /tmp/udfs /tmp/udfs"
su - sandbox -c "hadoop fs -chmod -R 777 /tmp/udfs"
su - sandbox -c "/usr/lib/hue/build/env/bin/hue install_udfs"
su - sandbox -c "/usr/lib/hue/build/env/bin/hue oozie_setup"
su - sandbox -c "/usr/lib/hue/build/env/bin/hue jobsub_setup"
su - sandbox -c "/usr/lib/hue/build/env/bin/hue beeswax_install_examples"
rm /tmp/udfs.tar.gz
rm  -rf /tmp/udfs
touch /root/.hdfs_prepared
/etc/init.d/hue restart
)
exit 0
