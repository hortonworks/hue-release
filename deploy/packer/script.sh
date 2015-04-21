#!/bin/bash
set -x
echo "convert vmware vmx files to ova"
ovftool packer_vmware/"Hortonworks Sandbox with HDP 2.2.4".vmx packer_vmware/vmware-iso.ova
echo "renaming and uploading to Amazon S3:"
name=Sandbox_HDP_2.2_VMWare_`date +"%d_%m_%Y_%H_%M_%S"`.ova
mv packer_vmware/vmware-iso.ova packer_vmware/$name

aws s3 cp packer_vmware/$name s3://dev.hortonworks.com/sandbox/BUILDS/


md5sum packer_vmware/$name | awk '{print $1}' > packer_vmware/$name.md5

aws s3 cp packer_vmware/$name.md5 s3://dev.hortonworks.com/sandbox/BUILDS/
