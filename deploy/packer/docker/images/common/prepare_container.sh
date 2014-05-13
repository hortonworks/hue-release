yum update -y
yum install -y openssh-server openssh-clients wget tar sudo perl java-1.7.0-openjdk-devel ntp
sed -ri 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
sed -i "s/#UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config
echo 'root:hadoop' | chpasswd 
echo "UseDNS no" >> /etc/ssh/sshd_config
echo "GSSAPIAuthentication no" >> /etc/ssh/sshd_config
cd /root
wget http://dev2.hortonworks.com.s3.amazonaws.com/stuff/ssh.tar.gz
tar xvf ssh.tar.gz
chown root:root -R .ssh
chmod 600 .ssh/id_rsa
chmod 700 .ssh
ln -s /root/.ssh/id_rsa /etc/ssh/ssh_host_rsa_key
rm -f ssh.tar.gz
#service iptables stop
#service ip6tables stop
#setenforce 0
echo 'export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk.x86_64; export PATH=$JAVA_HOME/bin:$PATH' > /etc/profile.d/java.sh;
perl -pi -e 's:/etc/hosts:/tmp/hosts:g' /lib64/libnss_files.so.2
#chconfig ip6tables off
#cd ../; rm -rf /tmp/*;
