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
MEM=4096
VERSION="2.0 Beta"

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

# BEGIN

if [ -z $1 ]; then
	TARGET=default
else
	TARGET="$1"
fi

echo "Using target '$TARGET'"

if ! which ovftool &>/dev/null; then
	echo >&2
	echo "WARNING: ovftool not found!" >&2
	echo "WARNING: VMware image can NOT be built" >&2
	echo >&2
fi

if [ ! -f .vagrant/machines/$TARGET/virtualbox/id ]; then
	echo "ERROR: No machine found" >&2
	echo "Please, deploy machine with Vagrant ($ vagrant up default)" >&2
	exit 1
fi

ID=`cat .vagrant/machines/$TARGET/virtualbox/id`
if ! VBoxManage showvminfo "$ID" &>/dev/null; then
	echo "ERROR: Machine not found in VirtualBox. Please, redeploy it with Vagrant" >&2
	exit 2
fi

vminfo $ID Name
MACHINE="$(vminfo $ID Name)"
HDDFILE="$(vmhdd $ID)"

if [[ ! "`vminfo $ID State`" == "running"* ]]; then
	echo "ERROR: Machine is not running" >&2
	exit 3
fi

# ======== VirtualBox ========
echo "VirtualBox preparing..."
echo "	. /virtualization"
vagrant ssh $TARGET -c "echo 'vbox' | sudo tee /virtualization" >/dev/null
echo -n "	. powering off.."
vagrant halt $TARGET >/dev/null
echo -n "."; sleep 5; echo "."; sleep 5
echo "	. Removing shared folders"
VBoxManage sharedfolder remove "$MACHINE" --name '/vagrant' &>/dev/null || true
VBoxManage sharedfolder remove "$MACHINE" --name '/tmp/vagrant-puppet/manifests' &>/dev/null || true
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
vagrant ssh $TARGET -c "sudo /opt/VBoxGuestAdditions-*/uninstall.sh" >/dev/null
echo "	. /virtualization"
vagrant ssh $TARGET -c "echo 'vmware' | sudo tee /virtualization" >/dev/null
echo -n "	. powering off.."
vagrant halt $TARGET >/dev/null
echo -n "."; sleep 5; echo "."; sleep 5

if which ovftool &>/dev/null; then
	echo "	. Copying vmdk file...";
	cp "$HDDFILE" ./vmware/sandbox.vmdk;
	FILENAME_VW="./Hortonworks Sandbox $VERSION VMware.ova";
	echo "	. Exporting...";
	ovftool "./vmware/Hortonworks Sandbox 2.0.vmx" "$FILENAME_VW";
	echo "VMware image done! `pwd`/$FILENAME_VW";
else
	echo "WARNING: Skipping VMware exporting due to missing ovftool" >&2;
fi

# ======== Hyper-V ========
echo
echo "Hyper-V preparing..."
echo "	. Booting..."
VBoxManage startvm $ID
sleep 90

echo "	. adding 'noapic' to kernel options..."
vagrant ssh $TARGET -c 'sudo sed -i /boot/grub/menu.lst -r -e "s/(kernel .*)$/\1 noapic/g"'
echo "	. /virtualization"
vagrant ssh $TARGET -c "echo 'hyper-v' | sudo tee /virtualization"
echo "	. powering off.."
vagrant halt $TARGET
echo -n "."; sleep 5; echo "."; sleep 5
echo "	. Cloning image VMDK to VHD..."
FILENAME_HV="./hyper-v/sandbox.vhd"
VBoxManage clonehd "$HDDFILE" "$FILENAME_HV" --format vhd
echo "Hyper-V HDD done! `pwd`/$FILENAME_HV"
