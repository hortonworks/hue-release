echo "# Do not remove the following line, or various programs" > /etc/hosts
echo "# that require network functionality will fail." >> /etc/hosts
echo "127.0.0.1		localhost.localdomain localhost" >> /etc/hosts

#echo "`ifconfig eth1 | grep "inet addr" | awk '{ print $2 }' | awk -F':' '{print $2}'`		`hostname`" >> /etc/hosts

function get_ip() {
	echo "`ip addr | grep 'inet ' | grep -v 127 | awk '{ print $2 }' | awk -F'/' '{print $1}'`"
}

HOST=$(get_ip)
NUM=1
while [ -z "$HOST" ]; do
	HOST=$(get_ip)
	sleep 5
	NUM=$(($NUM-1))
	if [ ! $NUM -gt 0 ]; then
		HOST="127.0.0.1"
		echo "Failed to update IP"
		break
	fi
done
echo "$HOST	`hostname`" >> /etc/hosts

