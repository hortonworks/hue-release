usermod -a -G users hdfs
usermod -a -G users hive
usermod -a -G users oozie
usermod -a -G users hcat
#TEMP
sed -i 's|logviewer.port: 8000|logviewer.port: 8005|g' /etc/storm/conf/storm.yam
