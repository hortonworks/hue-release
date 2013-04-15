#set -x
set -e

vagrant up
vagrant halt
MACHINE="$(VBoxManage list vms | grep `cat .vagrant/machines/default/virtualbox/id` | sed -r 's/\"(.*)\".*/\1/g')"
echo $MACHINE
VBoxManage modifyvm "$MACHINE" --memory 2048 --cpus 2
VBoxManage export "$MACHINE" --output "$MACHINE VirtualBox".ova \
    --vsys 0 --vendor "HortonWorks" --version "Caterpillar" --product "Sandbox"

HDDFILE="$(VBoxManage list hdds | grep -e "$MACHINE/" | sed -r "s/.*:[^/]*(.*)/\1/g")"
cp "$HDDFILE" ./vmware/sandbox.vmdk
ovftool ./vmware/vmware.vmx "./$MACHINE VMware.ova"
VBoxManage clonehd "$HDDFILE" ./hyper-v/sandbox.vhd --format vhd

