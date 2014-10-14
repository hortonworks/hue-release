#!/bin/bash
set -x
for i in 1 2 3 
do
	adduser -g IT        it${i}
	adduser -g Legal     legal${i}
	adduser -g Marketing mktg${i}
	adduser -g Network   network${i}
done

adduser guest

mkdir -p /home/knox
chown -R knox:knox /home/knox
