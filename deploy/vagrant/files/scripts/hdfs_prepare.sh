[ ! -f /root/.hdfs_prepared ] && (
su - hcat -c "hadoop dfs -copyFromLocal /usr/share/HDP-webhcat/pig.tar.gz /apps/webhcat/"
su - hcat -c "hadoop dfs -copyFromLocal /usr/share/HDP-webhcat/hive.tar.gz /apps/webhcat/"
su - hcat -c "hadoop dfs -copyFromLocal /usr/lib/hadoop/contrib/streaming/hadoop-streaming*.jar /apps/webhcat/"

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
