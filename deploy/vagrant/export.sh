#set -x
set -e

vagrant up
vagrant halt
MACHINE="$(VBoxManage list vms | grep `python2 -c "import json; print json.loads(file('.vagrant').read())['active']['default']"` | sed -r 's/\"(.*)\".*/\1/g')"
VBoxManage export "$MACHINE" --output "$MACHINE VirtualBox".ova --vsys 0 --vendor "HortonWorks" --version "Caterpillar" --product "Sandbox"

HDDFILE="$(VBoxManage list hdds | grep -e "$MACHINE/" | sed -r "s/.*:[^/]*(.*)/\1/g")"
cp "$HDDFILE" ./vmware/sandbox.vmdk
ovftool ./vmware/vmware.vmx "./$MACHINE VMware.ova"