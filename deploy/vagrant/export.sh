#set -x
set -e

# VBox
vagrant up
vagrant ssh -c "echo 'vbox' | sudo tee /virtualization"
vagrant halt
MACHINE="$(VBoxManage list vms | grep `cat .vagrant/machines/default/virtualbox/id` | sed -r 's/\"(.*)\".*/\1/g')"
echo $MACHINE
VBoxManage modifyvm "$MACHINE" --memory 2048 --cpus 2
VBoxManage export "$MACHINE" --output "$MACHINE VirtualBox".ova \
    --vsys 0 --vendor "HortonWorks" --version "1.3" --product "Sandbox"

# VMware
vagrant up --no-provision
vagrant ssh -c "sudo /opt/VBoxGuestAdditions-*/uninstall.sh"
vagrant ssh -c "echo 'vmware' | sudo tee /virtualization"
vagrant halt

HDDFILE="$(VBoxManage list hdds | grep -e "$MACHINE/" | sed -r "s/.*:[^/]*(.*)/\1/g")"
cp "$HDDFILE" ./vmware/sandbox.vmdk
ovftool "./vmware/Sandbox HDP Caterpillar.vmx" "./$MACHINE VMware.ova"

# Hyper-V
vagrant up --no-provision
vagrant ssh -c 'sudo sed -i /boot/grub/menu.lst -r -e "s/(kernel .*)$/\1 noapic/g"'
vagrant ssh -c "echo 'hyper-v' | sudo tee /virtualization"
vagrant halt
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
