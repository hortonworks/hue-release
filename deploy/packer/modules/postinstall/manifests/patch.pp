class postinstall::patch{
	#need to set some services in standby	
	file{'maintenance_script':
		ensure	=> file,
		path	=> "/tmp/put_in_maintenance.sh", 
		mode	=> '777',
		source	=> "puppet:///modules/postinstall/patch/put_services_in_maintenance.sh"
	}
	file{'restart_stale_hive':
		ensure	=> file, 
		path	=> "/tmp/restart_stale_hive.sh",
		mode	=> "777",
		source	=> "puppet:///modules/postinstall/patch/restart_stale_hive.sh",
	}
	exec{'put_maintenance':
		command	=> "bash -x /tmp/put_in_maintenance.sh",
		provider	=> 'shell',
		require	=>File['maintenance_script'],
		timeout	=> 0
	}
	exec{'BUG-34485':
		command	=> 'bash -x /tmp/restart_stale_hive.sh',
		provider	=> 'shell',
		require		=> File['restart_stale_hive'],
	}
	exec{'bug-34455':
		command	=> "cp /usr/share/java/mysql-connector-java.jar /usr/hdp/*/knox/ext/",
		provider	=> 'shell',
	}
	exec{'BUG-35799':
		command => 'ambari-agent stop && rm -f /var/lib/ambari-agent/data/structured-out-status.json',
		provider	=> 'shell'
	}
}
include postinstall::patch
