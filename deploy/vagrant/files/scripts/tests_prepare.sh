USER=hue

wget -O /tmp/TestData.tar.gz http://dl.dropbox.com/u/87847087/TestData.tar.gz
cd /tmp
tar xvf TestData.tar.gz
chown $USER TestData
usermod -a -G users $USER
su - $USER -c "hadoop fs -copyFromLocal /tmp/TestData /tmp/TestData"
su - $USER -c "hadoop fs -chmod -R 777 /tmp/TestData"
rm /tmp/TestData.tar.gz
rm  -rf /tmp/TestData
exit 0
