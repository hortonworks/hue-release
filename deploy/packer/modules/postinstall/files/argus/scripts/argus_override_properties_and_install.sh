#!/bin/bash

#Make sure this script is from where folder which contains the override files
#e.g. cd /vagrant/modules/postinstall/files/argus/install_overrides
install_overrides_folder=`pwd`

if [ ! -d admin ]; then
	echo "ERROR: This script should be run from override folder. e.g. /vagrant/modules/postinstall/files/argus/install_overrides"
	exit 1
fi

#latest_ver=`ls | grep -v current | sort -unr | head --lines=1`
latest_folder=`find /usr/hdp -name argus | grep -v current | sort -unr | head --lines=1`

echo "Override folder=$install_overrides_folder Install_folder=$latest_folder"

cd $install_overrides_folder
cp -r * $latest_folder

cd ${latest_folder}/admin
./install.sh

cd ${latest_folder}/ugsync
./install.sh

cd ${latest_folder}/hdfs-agent
./enable-hdfs-agent.sh

#  exec{"install_argus_admin":
#    cwd => "/usr/hdp/current/argus/admin",
#    command => "/usr/hdp/current/argus/admin/install.sh",
#    require => Exec["override_properties"],
#  }
#  
#  exec{"install_argus_user_sync":
#    cwd => "/usr/hdp/current/argus/ugsync",
#    command => "/usr/hdp/current/argus/ugsync/install.sh",
#    require => Exec["install_argus_admin"],
#  }
#   
#  exec{"install_argus_hdfs_agent":
#    cwd => "/usr/hdp/current/argus/hdfs-agent",
#    command => "/usr/hdp/current/argus/hdfs-agent/enable-hdfs-agent.sh",
#    require => Exec["install_argus_admin"],
#  } 
