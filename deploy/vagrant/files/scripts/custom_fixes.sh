usermod -a -G users hdfs
usermod -a -G users hive
usermod -a -G users oozie
usermod -a -G users hcat

echo "export HCAT_HOME=/usr/lib/hive-hcatalog" > /etc/profile.d/hcatalog.sh
