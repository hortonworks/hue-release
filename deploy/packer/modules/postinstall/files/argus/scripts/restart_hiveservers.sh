#/bin/bash
set -x
SCRIPTS_PATH="/usr/lib/hue/tools/start_scripts"

hive_pid=/var/run/hive/hive-server.pid


#Double sure HiveServer2 is down
echo "Stopping Hive ..."
ps aux | grep HiveServer2 | grep -v "grep" | awk '{print $2}' | xargs kill >/dev/null 2>&1

echo "Stopping MetaStore"
ps aux | grep MetaStore | grep -v "grep" | awk '{print $2}' | xargs kill >/dev/null 2>&1

#Let's wait for 10 seconds to make sure everything stops gracefully
sleep 10

#Kill Hive Server if it is running
if [ -f $hive_pid ]; then
	echo "Killing hiveserver2 by force..."
	kill `cat $hive_pid` 2> /dev/null
	sleep 10
	if [ -f $hive_pid ]; then
		kill -9 `cat $hive_pid` 2> /dev/null
	fi
fi


#Starting MetaStore
#make --makefile $SCRIPTS_PATH/start_deps.mf -B hive -j -i
#HiveServer2 will start MetaServer also

#Starting HiveServe2
make --makefile $SCRIPTS_PATH/start_deps.mf -B hive2 -j -i

sleep 60