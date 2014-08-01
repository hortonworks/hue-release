yum update -y
yum install -y yum-utils wget redhat-lsb
mkdir /tmp/install
chmod 700 /tmp/install
printf 'To login to the the shell, use:\nusername: root\npassword: hadoop\n' >> /etc/issue
reboot && sleep 150
