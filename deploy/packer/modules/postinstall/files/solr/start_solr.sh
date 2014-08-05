#!/bin/bash

cd /opt/solr/solr/hdp
nohup java -jar start.jar >> /var/log/solr.log 2>> /var/log/solr.err &
echo $! > /var/run/solr.pid
echo "Started Solr! PID `cat /var/run/solr.pid`"
echo "Logging to /var/log/solr.log and /var/log/solr.err"
