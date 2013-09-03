import "sandbox_full.pp"

class test_data {
	include sandbox

	file { 'tests_prepare.sh':
		path    => "/tmp/tests_prepare.sh",
		content => template("/vagrant/files/scripts/tests_prepare.sh"),
	}
	
	exec { "tests_prepare.sh":
		command => '/bin/bash /tmp/tests_prepare.sh > /var/log/test_prepare.log',
		require => [File['tests_prepare.sh'], Exec["start"]],
		timeout => 0
	}
}

include test_data