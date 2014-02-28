#!/bin/bash

set -e
# Script for exporting machines to VirtualBox, VMware and Hyper-V formats
# first argument: Vagrant machine target [if not specified, script uses "default"]

# Before executing export.sh ensure your VM is running

if [[ "$OSTYPE" == "darwin"* ]]; then
	SED="sed -E"
else
	SED="sed -r"
fi

# memory amount in MB for VirtualBox machine
MEM=2048
VERSION="2.1"

if [ -z $1 ]; then
	TARGET=default
else
	TARGET="$1"
fi

if [ "$TARGET" == "clean" ]; then
	echo "Cleaning artifacts"
	rm -f *.ova
	rm -f "hyper-v/sandbox.vhd"
	echo "Clean done"
	exit 0
fi

_SSH="vagrant ssh $TARGET -c"

# Returns property from vminfo
# Arguments:
# 	$1 machine UUID
#	$2 property name
function vminfo() {
	VBoxManage showvminfo "$1" | grep "^$2:" | head -n 1 | $SED "s/[^:]*:[ \t]*(.*)$/\1/g"
}

# Returns path to VMDK hard disk of machine
# Arguments:
# 	$1 machine UUID
function vmhdd() {
	VBoxManage showvminfo "$1" | grep vmdk | $SED "s/[^:]*: (.*) \(.*/\1/g"
}

function poweroff_target() {
	(set +e; vagrant halt $TARGET >/dev/null; true)
}

# Prints $1 to stderr
function echoerr() {
	echo "$1" >&2
}

# BEGIN

echo "Using target '$TARGET'"

if ! which ovftool &>/dev/null; then
	echoerr
	echoerr "WARNING: ovftool not found!"
	echoerr "WARNING: VMware image can NOT be built"
	echoerr
fi

if [ ! -f .vagrant/machines/$TARGET/virtualbox/id ]; then
	echoerr "ERROR: No machine found"
	echoerr "Please, deploy machine with Vagrant ($ vagrant up default)"
	exit 1
fi

ID=`cat .vagrant/machines/$TARGET/virtualbox/id`
if ! VBoxManage showvminfo "$ID" &>/dev/null; then
	echoerr "ERROR: Machine not found in VirtualBox. Please, redeploy it with Vagrant"
	exit 2
fi

vminfo $ID Name
MACHINE="$(vminfo $ID Name)"
HDDFILE="$(vmhdd $ID)"

if [[ ! "`vminfo $ID State`" == "running"* ]]; then
	echoerr "ERROR: Machine is not running"
	exit 3
fi

# ======== VirtualBox ========
echo "VirtualBox preparing..."
echo "	. /virtualization"
$_SSH "echo 'vbox' | sudo tee /virtualization" >/dev/null
echo -n "	. powering off.."
poweroff_target
echo -n "."; sleep 5; echo "."; sleep 5
echo "	. Removing shared folders"
VBoxManage sharedfolder remove "$MACHINE" --name '/vagrant' &>/dev/null || true
VBoxManage sharedfolder remove "$MACHINE" --name '/tmp/vagrant-puppet/manifests' &>/dev/null || true
VBoxManage sharedfolder remove "$MACHINE" --name '/tmp/vagrant-puppet-1/manifests' &>/dev/null || true
echo "	. Customizations [RAM $MEM MB]"
VBoxManage modifyvm "$MACHINE" --memory $MEM --cpus 2
echo "	. Exporting..."
FILENAME_VB="Hortonworks Sandbox $VERSION VirtualBox.ova"
VBoxManage export "$MACHINE" --output "$FILENAME_VB" \
    --vsys 0 --vendor "Hortonworks" --version "$VERSION" --product "Sandbox"

echo "VirtualBox image done! `pwd`/$FILENAME_VB"

# ======== VMware ========
echo
echo "VMware preparing..."
echo "	. Booting..."
vagrant up $TARGET --no-provision >/dev/null
echo "	. Uninstalling VBoxGuestAdditions"
$_SSH "sudo /opt/VBoxGuestAdditions-*/uninstall.sh" >/dev/null
echo "	. /virtualization"
$_SSH "echo 'vmware' | sudo tee /virtualization" >/dev/null
echo "	. setting up vmware-tools"
$_SSH "sudo bash /usr/libexec/vmware-tools.sh" >/dev/null
echo -n "	. powering off.."
poweroff_target
echo -n "."; sleep 5; echo "."; sleep 5

if which ovftool &>/dev/null; then
	echo "	. Copying vmdk file...";
	cp "$HDDFILE" ./vmware/sandbox.vmdk;
	FILENAME_VW="./Hortonworks Sandbox $VERSION VMware.ova";
	echo "	. Exporting...";
	ovftool "./vmware/Hortonworks Sandbox 2.0.vmx" "$FILENAME_VW";
	echo "VMware image done! `pwd`/$FILENAME_VW";
else
	echoerr "WARNING: Skipping VMware exporting due to missing ovftool"
fi

# ======== Hyper-V ========
echo
echo "Hyper-V preparing..."
echo "	. Booting..."
VBoxManage startvm $ID
sleep 90

echo "	. adding 'noapic' to kernel options..."
$_SSH 'sudo sed -i /boot/grub/menu.lst -r -e "s/(kernel .*)$/\1 noapic/g"'
echo "	. /virtualization"
$_SSH "echo 'hyper-v' | sudo tee /virtualization"
echo "	. set static IP"
$_SSH 'sudo sed -i "s/dhcp/static\nIPADDR=192.168.56.101\nNETMASK=255.255.255.0\nGATEWAY=192.168.56.1/g" /etc/sysconfig/network-scripts/ifcfg-eth0'
echo "	. disabling DHCP client"
$_SSH 'sudo sed -i "s/dhclient/#dhclient/g" /etc/init.d/startup_script'
echo "	. removing vmware-tools"
$_SSH "sudo bash /usr/libexec/vmware-tools.sh remove" >/dev/null
echo "	. powering off.."
poweroff_target
echo -n "."; sleep 5; echo "."; sleep 5
echo "	. Cloning image VMDK to VHD..."
FILENAME_HV="./hyper-v/sandbox.vhd"
VBoxManage clonehd "$HDDFILE" "$FILENAME_HV" --format vhd
echo "Hyper-V HDD done! `pwd`/$FILENAME_HV"
