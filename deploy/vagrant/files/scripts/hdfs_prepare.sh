[ ! -f /root/.hdfs_prepared ] && (
su - hdfs -c "hadoop fs -rmr -skipTrash /user/ambari_qa/.staging/"
su - hdfs -c "hadoop fs -rm -skipTrash /apps/webhcat/pig.tar.gz"
wget -O /tmp/pig.tar.gz https://www.dropbox.com/s/mkvv1xz89i5ykyt/pig.tar.gz
su - hcat -c "hadoop fs -put /tmp/pig.tar.gz /apps/webhcat/pig.tar.gz"
su - hcat -c "hadoop fs -chmod 755 /apps/webhcat/pig.tar.gz"
rm -f /tmp/pig.tar.gz
echo "Installing udfs"
wget -O /tmp/udfs.tar.gz https://www.dropbox.com/s/8wx2pops8xw2kd8/udfs.tar.gz
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
)
exit 0
