#!/bin/bash

rpm --import http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-DSA-KEY.pub
rpm --import http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-RSA-KEY.pub

cat > /etc/yum.repos.d/vmware-tools.repo << EOF
[vmware-tools]
name=VMware Tools for Red Hat Enterprise Linux $releasever – $basearch
baseurl=http://packages.vmware.com/tools/esx/latest/rhel6/\$basearch
enabled=1
gpgcheck=1
gpgkey=http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-RSA-KEY.pub
EOF

yum -y install vmware-tools-esx-kmods
yum -y install vmware-tools-core vmware-tools-esx-nox
