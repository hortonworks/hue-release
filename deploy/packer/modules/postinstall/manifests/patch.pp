class postinstall::patch{
	#need to set some services in standby	
	file{'maintenance_script':
		ensure	=> file,
		path	=> "/tmp/put_in_maintenance.sh", 
		mode	=> '777',
		source	=> "puppet:///modules/postinstall/put_services_in_maintenance.sh"
	}

	exec{'put_maintenance':
		command	=> "bash -x /tmp/put_in_maintenance.sh",
		provider	=> 'shell',
		require	=>File['maintenance_script'],
		timeout	=> 0
	}
	exec{'bug-34455':
		command	=> "cp /usr/share/java/mysql-connector-java.jar /usr/hdp/*/knox/ext/",
		provider	=> 'shell',
	}
	file{'stale_hive':
		path	=> '/tmp/stale_hive.json',
		source	=> 'puppet:///modules/postinstall/patch/stale_hive.json'
		
	}
	exec{'stale_hive_restart':
		require	=> File['stale_hive'],
		provider	=> 'shell',
		command		=> 'curl -i --header "Accept:application/json" -H "Content-Type: application/json" -X POST -u admin:admin http://127.0.0.1:8080/api/v1/clusters/Sandbox/requests -d @/tmp/stale_hive.json'
	}
}
#include postinstall::patch
