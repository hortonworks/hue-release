#/bin/bash

set -x
SCRIPTS_PATH="/usr/lib/hue/tools/start_scripts"

echo "Stop HBase"
# slave node
echo "Stop Hbase RegionServers"
su -l hbase -c "/usr/hdp/current/hbase-regionserver/bin/hbase-daemon.sh --config /etc/hbase/conf stop regionserver"

# master node
echo "Stop Hbase Master"
su -l hbase -c "/usr/hdp/current/hbase-master/bin/hbase-daemon.sh --config /etc/hbase/conf stop master"

#Starting HBase Master and Region Servers
#make --makefile $SCRIPTS_PATH/start_deps.mf -B hbase_master -j -i
#make --makefile $SCRIPTS_PATH/start_deps.mf -B hbase_regionservers -j -i
#service hbase-starter stop
#service hbase-starter start

su -l hbase -c "/usr/hdp/current/hbase-master/bin/hbase-daemon.sh --config /etc/hbase/conf start master"

su -l hbase -c "/usr/hdp/current/hbase-regionserver/bin/hbase-daemon.sh --config /etc/hbase/conf start regionserver"

sleep 30