#!/bin/bash -eux

echo "Fixing slow DNS issue"

if [[ "$PACKER_BUILDER_TYPE" == virtualbox* ]]; then
    ## https://access.redhat.com/site/solutions/58625 (subscription required)
    # add 'single-request-reopen' so it is included when /etc/resolv.conf is generated
    echo 'RES_OPTIONS="single-request-reopen"' >> /etc/sysconfig/network
    service network restart
    echo 'Slow DNS fix applied (single-request-reopen)'
else
    echo 'Slow DNS fix not required for this platform, skipping'
fi

echo "# File is generated from ${SCRIPT}" > /etc/hosts
echo "# Do not remove the following line, or various programs" >> /etc/hosts
echo "# that require network functionality will fail." >> /etc/hosts
echo "127.0.0.1		localhost.localdomain localhost" >> /etc/hosts

function get_ip() {
    ip addr | grep 'inet ' | grep -v -E " lo" | awk '{ print $2 }' | awk -F'/' '{print $1}'
}


echo "Setup hostname"
HOST=$(get_ip)
NUM=5
while [ -z "$HOST" ]; do
    HOST=$(get_ip)
    sleep 5
    NUM=$(($NUM-1))
    if [ $NUM -le 0 ]; then
	HOST="127.0.0.1"
	echo "Failed to update IP"
	break
    fi
done
echo "$HOST	sandbox.hortonworks.com ambari.hortonworks.com" >> /etc/hosts
hostname sandbox.hortonworks.com

echo 0 > /proc/sys/kernel/hung_task_timeout_secs

sed -i -e '/NM_CONTROLLED/d' /etc/sysconfig/network-scripts/ifcfg-eth0
echo 'NM_CONTROLLED=no' >> /etc/sysconfig/network-scripts/ifcfg-eth0
echo 'PEERDNS=no' >> /etc/sysconfig/network-scripts/ifcfg-eth0
