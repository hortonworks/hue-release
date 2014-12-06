#!/bin/bash
set -x

function createUser {
	group=$1
	user=$2
	
	adduser -g $group $user
	
	#create hadoop log folder and change ownership
	mkdir -p /var/log/hadoop/$user
	chmod 777 /var/log/hadoop/$user
	chown $user /var/log/hadoop/$user
}

for i in 1 2 3 
do
	createUser IT it${i}
	createUser Legal     legal${i}
	createUser Marketing mktg${i}
	createUser Network   network${i}
	

done

createUser guest guest
usermod -G users guest

mkdir -p /home/knox
chown -R knox:knox /home/knox

service ranger-usersync stop
service ranger-usersync start

