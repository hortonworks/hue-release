#!/bin/bash
#if [ "${LOGNAME}" != "hdfs" ]
#then
	#echo "ERROR: please login as hdfs and run this script."
	#exit 1
#fi

set -x
cd `dirname $0`

FS_ROOT=demo_data
HDFS_ROOT=/demo/data

hdfs dfs -rm -r -skipTrash ${HDFS_ROOT}

dirs="`find ${FS_ROOT} -type d -print | sed -e "s:^${FS_ROOT}:${HDFS_ROOT}:"`"
for d in ${dirs}
do
	hdfs dfs -mkdir -p $d
done


files="`find ${FS_ROOT} -type f -print`"
for f in ${files}
do
	fn=`echo $f | sed -e "s:^${FS_ROOT}:${HDFS_ROOT}:"`
	hdfs dfs -copyFromLocal $f $fn
done

hdfs dfs -chown -R hdfs:hdfs ${HDFS_ROOT}

hdfs dfs -chmod -R 700 ${HDFS_ROOT}

#hdfs dfs -ls -R ${HDFS_ROOT}
