#!/bin/bash

rpm --import http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-DSA-KEY.pub
rpm --import http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-RSA-KEY.pub

cat > /etc/yum.repos.d/vmware-tools.repo << EOF
[vmware-tools]
name=VMware Tools
baseurl=http://packages.vmware.com/tools/esx/5.1latest/rhel6/\$basearch
enabled=1
gpgcheck=1
EOF

yum -y install vmware-tools-core vmware-tools-esx-nox
