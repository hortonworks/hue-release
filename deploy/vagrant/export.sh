set -x
set -e

platform='unknown'
unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
   platform='linux'
elif [[ "$unamestr" == 'FreeBSD' ]]; then
   platform='freebsd'
fi

[ -z $1 ] && MACHINE_VERSION=default || MACHINE_VERSION="$1"

# VBox
#vagrant up
if [[ "$OSTYPE" == "darwin"* ]]; then
	MACHINE="$(VBoxManage list vms | grep `cat .vagrant/machines/$MACHINE_VERSION/virtualbox/id` | sed -E 's/\"(.*)\".*/\1/g')"
else
	MACHINE="$(VBoxManage list vms | grep `cat .vagrant/machines/$MACHINE_VERSION/virtualbox/id` | sed -r 's/\"(.*)\".*/\1/g')"
fi

vagrant ssh $MACHINE_VERSION -c "echo 'vbox' | sudo tee /virtualization"
vagrant halt $MACHINE_VERSION
VBoxManage sharedfolder remove "$MACHINE" --name '/vagrant'
VBoxManage sharedfolder remove "$MACHINE" --name '/tmp/vagrant-puppet/manifests'
echo $MACHINE
VBoxManage modifyvm "$MACHINE" --memory 2048 --cpus 2
VBoxManage export "$MACHINE" --output "Hortonworks-Sandbox-1.3-VirtualBox".ova \
    --vsys 0 --vendor "HortonWorks" --version "1.3" --product "Sandbox"

# VMware
vagrant up $MACHINE_VERSION --no-provision
vagrant ssh $MACHINE_VERSION -c "sudo /opt/VBoxGuestAdditions-*/uninstall.sh"
vagrant ssh $MACHINE_VERSION -c "echo 'vmware' | sudo tee /virtualization"
vagrant halt $MACHINE_VERSION

if [[ "$OSTYPE" == "darwin"* ]]; then
	HDDFILE="$(VBoxManage list hdds | grep -e "$MACHINE/" | sed -E "s/.*:[^/]*(.*)/\1/g")"
else
	HDDFILE="$(VBoxManage list hdds | grep -e "$MACHINE/" | sed -r "s/.*:[^/]*(.*)/\1/g")"
fi
cp "$HDDFILE" ./vmware/sandbox.vmdk
ovftool "./vmware/Hortonworks Sandbox 1.3.vmx" "./Hortonworks-Sandbox-1.3-VMware.ova"

# Hyper-V
vagrant up $MACHINE_VERSION --no-provision
vagrant ssh $MACHINE_VERSION -c 'sudo sed -i /boot/grub/menu.lst -r -e "s/(kernel .*)$/\1 noapic/g"'
vagrant ssh $MACHINE_VERSION -c "echo 'hyper-v' | sudo tee /virtualization"
vagrant halt $MACHINE_VERSION
VBoxManage clonehd "$HDDFILE" ./hyper-v/sandbox.vhd --format vhd

exit 0

mkdir -p ./winshared
sudo mount -t cifs //25.84.118.43/share -o uid=1000,gid=1000,username=Administrator,password='had1029oop!' ./winshared
cp ./hyper-v/sandbox.vhd ./winshared/sandbox.vhd

# needs on windows server
#   - pscx.codeplex.com
#   - pshyperv.codeplex.com

./hyper-v/rps.py -h 25.84.118.43 -k ./hyper-v/key -s -- << EOF
Import-Module HyperV
New-VM '$MACHINE'
Add-VMDisk '$MACHINE' -Path '%UserProfile%\Share\sandbox.vhd'
Set-VMMemory '$MACHINE' -Memory 2GB
Set-VMCPUCount '$MACHINE' -CPUCount 2
EOF

./hyper-v/rps.py -h 25.84.118.43 -k ./hyper-v/key -s -- << EOF
Import-Module HyperV
rm -R 'C:\Exported'
Export-VM '$MACHINE' -Path 'C:\Exported\' -Wait -CopyState
Get-ChildItem 'C:\Exported\' -R -Exclude '*.vhd' | Copy-Item -Destination '%UserProfile%\Share\\$MACHINE'
EOF

cp -R "./winshared/$MACHINE" ./
mv ./hyper-v/sandbox.vhd "./winshared/$MACHINE/"
