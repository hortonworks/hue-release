#!/bin/bash

RAM=$(grep MemTotal /proc/meminfo | awk '{print $2}')
if [ $RAM -gt 1572864 -a $RAM -lt 3670016 ]; then # 1.5GB < RAM < 3.5GB
  modprobe zram num_devices=2 # by cpu count
  SIZE=536870912 # 512mb
  echo $SIZE > /sys/block/zram0/disksize
  mkswap /dev/zram0
  echo $SIZE > /sys/block/zram1/disksize
  mkswap /dev/zram1
  swapon -p 100 /dev/zram0
  swapon -p 100 /dev/zram1
fi
