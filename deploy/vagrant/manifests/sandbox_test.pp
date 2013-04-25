import "sandbox.pp"

class test_data {
	package { "wget":
		ensure => present,
	}
	
	file { 'tests_prepare.sh':
		path    => "/tmp/tests_prepare.sh",
		content => template("files/scripts/tests_prepare.sh"),
	}
	
	exec { "tests_prepare.sh":
		command => '/bin/bash /tmp/tests_prepare.sh > /var/log/test_start.log',
		require => [File['tests_prepare.sh'], Exec["start"]],
		timeout => 0
	}
}