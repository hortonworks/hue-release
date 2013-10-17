usermod -a -G users hdfs
usermod -a -G users hive
usermod -a -G users oozie
usermod -a -G users hcat

# quiet booting
sed -E -i.bak 's/^(\tkernel.*)$/\1 quiet/g' menu.lst
