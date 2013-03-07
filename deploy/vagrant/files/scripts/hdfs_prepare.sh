[ ! -f /root/.hdfs_prepared ] && (
su - hdfs -c "hadoop fs -rmr -skipTrash /user/ambari_qa/.staging/"
su - hdfs -c "hadoop fs -rm -skipTrash /apps/webhcat/pig.tar.gz"
wget -O /tmp/pig.tar.gz https://www.dropbox.com/s/mkvv1xz89i5ykyt/pig.tar.gz 
su - hcat -c "hadoop fs -put /tmp/pig.tar.gz /apps/webhcat/pig.tar.gz"
su - hcat -c "hadoop fs -chmod 755 /apps/webhcat/pig.tar.gz"
rm -f /tmp/pig.tar.gz
touch /root/.hdfs_prepared
)