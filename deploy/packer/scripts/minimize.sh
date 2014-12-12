#!/bin/sh -eux
#clean wget cache
rm -rf /var/cache/wget/*

#clean docs
rm -rf /usr/share/doc/*
rm -rf /tmp/packer-puppet-masterless
rm -rf /tmp/install
yum -y clean all
for dir in `mount | grep ext | awk '{ print $3 }'`; do
    echo "... $dir"
    dd if=/dev/zero >> "$dir/zero" 2>/dev/null
    rm -f "$dir/zero";
    echo "DONE"
    echo
done
# Block until the empty file has been removed, otherwise, Packer
# will try to kill the box while the disk is still full and that's bad
sync
