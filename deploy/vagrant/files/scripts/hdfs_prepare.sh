USER=hue

[ ! -f /root/.hdfs_prepared ] && (
su - hcat -c "hadoop dfs -copyFromLocal /usr/share/HDP-webhcat/pig.tar.gz /apps/webhcat/"
su - hcat -c "hadoop dfs -copyFromLocal /usr/share/HDP-webhcat/hive.tar.gz /apps/webhcat/"
su - hcat -c "hadoop dfs -copyFromLocal /usr/lib/hadoop/contrib/streaming/hadoop-streaming*.jar /apps/webhcat/"
su - hdfs -c "hadoop fs -chown -R hcat /apps/webhcat/"
su - hdfs -c "hadoop fs -chmod -R 777 /apps/webhcat/"


echo "Installing udfs"
wget -O /tmp/udfs.tar.gz http://dev2.hortonworks.com.s3.amazonaws.com/hdfs/pig/udfs.tar.gz
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
