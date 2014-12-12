#!/bin/bash -eux
# These were only needed for building VMware/Virtualbox extensions:
yum -y remove gcc cpp kernel-devel kernel-headers perl
package-cleanup --oldkernels --count=1 -y
yum -y clean all
rm -rf VBoxGuestAdditions_*.iso VBoxGuestAdditions_*.iso.?

# clean up redhat interface persistence
rm -f /etc/udev/rules.d/70-persistent-net.rules
sed -i 's/^HWADDR.*$//' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i 's/^UUID.*$//' /etc/sysconfig/network-scripts/ifcfg-eth0

# Manually delete all but en_US locales
find /usr/share/locale -maxdepth 1 -mindepth 1 -type d | grep -v -e "en_US" | xargs rm -rf

# Delete unused locales from local-archive
localedef --list-archive | grep -v -e "en_US" | xargs localedef --delete-from-archive
mv /usr/lib/locale/locale-archive /usr/lib/locale/locale-archive.tmpl
build-locale-archive


