echo "# Do not remove the following line, or various programs" > /etc/hosts
echo "# that require network functionality will fail." >> /etc/hosts
echo "127.0.0.1		localhost.localdomain localhost" >> /etc/hosts

#echo "`ifconfig eth1 | grep "inet addr" | awk '{ print $2 }' | awk -F':' '{print $2}'`		`hostname`" >> /etc/hosts

function get_inet_iface(){
	route | grep default | awk '{print $8}'
}


function get_ip() {
	ip addr | grep 'inet ' | grep -v -E "( lo| $(get_inet_iface))" | awk '{ print $2 }' | awk -F'/' '{print $1}'
}


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
echo "$HOST	`hostname`" >> /etc/hosts

echo 0 > /proc/sys/kernel/hung_task_timeout_secs
ethtool -K eth0 tso off
ethtool -K eth1 tso off
