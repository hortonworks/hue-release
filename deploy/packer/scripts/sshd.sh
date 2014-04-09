#!/bin/bash -eux

echo "UseDNS no" >> /etc/ssh/sshd_config
echo "GSSAPIAuthentication no" >> /etc/ssh/sshd_config
cd /root
wget http://dev2.hortonworks.com.s3.amazonaws.com/stuff/ssh.tar.gz
tar xvf ssh.tar.gz
