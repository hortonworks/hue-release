#!/bin/bash

#Make sure this script is run from the folder which contains the override files
#e.g. cd /tmp/argus/install_overrides
install_overrides_folder=`pwd`
scripts_folder=${install_overrides_folder}/../scripts

if [ ! -d admin ]; then
	echo "ERROR: This script should be run from override folder. e.g. /tmp/argus/install_overrides"
	exit 1
fi

#latest_ver=`ls | grep -v current | sort -unr | head --lines=1`
latest_folder=`find /usr/hdp -name argus | grep -v current | sort -unr | head --lines=1`

if [ -f /etc/profile.d/java.sh ]; then
	. /etc/profile.d/java.sh
fi

echo "Override folder=$install_overrides_folder Install_folder=$latest_folder JAVA_HOME=$JAVA_HOME"

set -x
cd $install_overrides_folder
cp -r * $latest_folder

cd ${latest_folder}/admin
./install.sh

cd ${latest_folder}/usersync
./install.sh

cd ${latest_folder}/hdfs-agent
./enable-hdfs-agent.sh

cd ${latest_folder}/hive-agent
./enable-hive-agent.sh
cp /etc/hive/conf/xa* /etc/hive/conf.server
cp /etc/hive/conf/hiveserver2-site.xml /etc/hive/conf.server
chmod hive:hadoop /etc/hive/conf.server/hiveserver2-site.xml

cd ${latest_folder}/hbase-agent
./enable-hbase-agent.sh

cd ${latest_folder}/knox-agent
./enable-knox-agent.sh

#cd ${latest_folder}/storm-agent
#./enable-storm-agent.sh

#Apply the patches
cd $install_overrides_folder
cd ../patches
#Resolve hue getting databases issues. Should be removed later as it is fixed by dev team
#./patch_for_audit_log_message/apply_patch.sh 


#Set the properties in Hive and HBase to use Argus
cd /var/lib/ambari-server/resources/scripts
#./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hive-site "hive.security.authorization.enabled" "true"
#./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hive-site "hive.security.authorization.manager" "com.xasecure.authorization.hive.authorizer.XaSecureHiveAuthorizerFactory"
#./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hive-site "hive.security.authenticator.manager" "org.apache.hadoop.hive.ql.security.SessionStateUserAuthenticator"

./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hbase-site "hbase.coprocessor.master.classes" "com.xasecure.authorization.hbase.XaSecureAuthorizationCoprocessor"
./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hbase-site "hbase.coprocessor.region.classes" "com.xasecure.authorization.hbase.XaSecureAuthorizationCoprocessor"

#Override the HiveServer2 startup template used by Ambari
#cd $install_overrides_folder
#cd ../hive_override
#hive_startup_template=/var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/HIVE/package/templates/startHiveserver2.sh.j2
#cp $hive_startup_template ${hive_startup_template}.$(date +%m%d%y%H%M).by_ranger
#cp startHiveserver2.sh.j2 $hive_startup_template


#Restart all the servers
#NameNode
#$scripts_folder/restart_namenode.sh

#HiveServer2
#$scripts_folder/restart_hiveservers.sh

#HBase
#$scripts_folder/restart_hbase.sh

#Copy the tutorial files to the home folder of root
cd $install_overrides_folder
cp -r ../argus_tutorial /root

