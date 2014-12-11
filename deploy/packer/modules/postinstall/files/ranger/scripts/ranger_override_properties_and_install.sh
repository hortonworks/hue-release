#!/bin/bash

#Make sure this script is run from the folder which contains the override files
#e.g. cd /tmp/ranger/install_overrides
install_overrides_folder=`pwd`
scripts_folder=${install_overrides_folder}/../scripts
admin_conf_overrides_folder=${install_overrides_folder}/../admin_conf_overrides
audit_setup_folder=${install_overrides_folder}/../audit_setup

if [ ! -d ranger-admin ]; then
	echo "ERROR: This script should be run from override folder. e.g. /tmp/ranger/install_overrides"
	exit 1
fi

#latest_ver=`ls | grep -v current | sort -unr | head --lines=1`
latest_admin_folder=`find /usr/hdp -name ranger-admin | grep -v current | sort -unr | head --lines=1`
latest_folder=${latest_admin_folder}/..

if [ -f /etc/profile.d/java.sh ]; then
	. /etc/profile.d/java.sh
fi

echo "Override folder=$install_overrides_folder Install_folder=$latest_folder JAVA_HOME=$JAVA_HOME"

set -x
cd $install_overrides_folder
cp -r * $latest_folder

cd ${latest_folder}/ranger-admin
./setup.sh
cp -r ${admin_conf_overrides_folder}/* /etc/ranger/admin/conf
service ranger-admin start

cd ${latest_folder}/ranger-usersync
./setup.sh
service ranger-usersync start

cd ${latest_folder}/ranger-hdfs-plugin
./enable-hdfs-plugin.sh
sed -i -e s/30000/5000/g /etc/hadoop/conf/xasecure-hdfs-security.xml

cd ${latest_folder}/ranger-hive-plugin
./enable-hive-plugin.sh
#sed -i -e s/30000/5000/g /etc/hive/conf/xasecure-hive-security.xml
#cp /etc/hive/conf/xa* /etc/hive/conf.server
#sed -i -e s/30000/5000/g
#cp /etc/hive/conf/hiveserver2-site.xml /etc/hive/conf.server
#chown hive:hadoop /etc/hive/conf.server/hiveserver2-site.xml
sed -i -e s/30000/5000/g /etc/hive/conf.server/xasecure-hive-security.xml

cd ${latest_folder}/ranger-hbase-plugin
./enable-hbase-plugin.sh
sed -i -e s/30000/5000/g /etc/hbase/conf/xasecure-hbase-security.xml

cd ${latest_folder}/ranger-knox-plugin
./enable-knox-plugin.sh
sed -i -e s/30000/5000/g /etc/knox/conf/xasecure-knox-security.xml

#cd ${latest_folder}/ranger-storm-plugin
#./enable-storm-plugin.sh

#Apply the patches
cd $install_overrides_folder
cd ../patches
#Resolve hue getting databases issues. Should be removed later as it is fixed by dev team
#./patch_for_audit_log_message/apply_patch.sh


#Set the properties in Hive and HBase to use Ranger
cd /var/lib/ambari-server/resources/scripts
#./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hive-site "hive.security.authorization.enabled" "true"
#./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hive-site "hive.security.authorization.manager" "com.xasecure.authorization.hive.authorizer.XaSecureHiveAuthorizerFactory"
#./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hive-site "hive.security.authenticator.manager" "org.apache.hadoop.hive.ql.security.SessionStateUserAuthenticator"
./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hive-site "hive.server2.enable.doAs" "false"

./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hbase-site "hbase.coprocessor.master.classes" "com.xasecure.authorization.hbase.XaSecureAuthorizationCoprocessor"
./configs.sh -u admin -p admin -port 8080 set sandbox.hortonworks.com Sandbox hbase-site "hbase.coprocessor.region.classes" "com.xasecure.authorization.hbase.XaSecureAuthorizationCoprocessor"



#Override the HiveServer2 startup template used by Ambari
#cd $install_overrides_folder
#cd ../hive_override
#hive_startup_template=/var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/HIVE/package/templates/startHiveserver2.sh.j2
#cp $hive_startup_template ${hive_startup_template}.$(date +%m%d%y%H%M).by_ranger
#cp startHiveserver2.sh.j2 $hive_startup_template


#Setup for auditing to HDFS

${audit_setup_folder}/create_hdfs_folders_for_audit.sh
#Need to run this after the repository is created. So moved this running during setup tutorial
#${audit_setup_folder}/set_audit_policies.sh http://localhost:6080 sandbox_hdfs admin admin


#Restart all the servers
#NameNode
#$scripts_folder/restart_namenode.sh

#HiveServer2
#$scripts_folder/restart_hiveservers.sh

#HBase
#$scripts_folder/restart_hbase.sh

#Copy the tutorial files to the home folder of root
cd $install_overrides_folder
cp -r ../ranger_tutorial /root
