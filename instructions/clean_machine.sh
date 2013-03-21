#!/bin/bash

rm -f /var/log/startup_script.log
rm -rf /var/log/hadoop/{hdfs,mapred}/*
rm -rf /var/log/{hive,hbase,audit,webhcat,oozie}/*

rm -f /tmp/hive-default-*
rm -rf /tmp/{tmp*,pig*tmp,Jetty_*}
rm -rf /tmp/hadoop-{hcat,hive,mapred,nagios,sandbox}/*

rm -rf /var/cache/yum
rm -rf /usr/share/man
echo "Files cleaned."

[ "z$1" = "zfiles" ] || bash ./zero_machine.sh

echo "Machine is clean now."
