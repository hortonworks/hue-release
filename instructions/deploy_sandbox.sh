#!/bin/bash

yum install git ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi gcc gcc-c++ krb5-devel libxml2-devel libxslt-devel mysql  mysql-devel openldap-devel python-devel python-simplejson sqlite-devel
useradd sandbox
su - sandbox
cd /home/sandbox
wget -O .ssh.tar.gz https://dl.dropbox.com/s/y4ae019z6944vn3/.ssh.tar.gz?dl=1
tar xvf .ssh.tar.gz
chmod 600 .ssh/id_rsa
rm .shh.tar.gz
wget http://mirrors.besplatnyeprogrammy.ru/apache/maven/maven-3/3.0.4/binaries/apache-maven-3.0.4-bin.tar.gz
tar xvf apache-maven-3.0.4-bin.tar.gz
rm apache-maven-3.0.4-bin.tar.gz
export PATH=$PATH:/home/sandbox/apache-maven-3.0.4/bin/
echo "Cloning hue ..."
git clone git@bitbucket.org:qwerty_nor/sandbox.git hue
echo "Cloning sandbox apps ..."
git clone git@github.com:hortonworks/sandbox-shared.git
echo "clonning tutorials ..."
git clone git@github.com:hortonworks/sandbox-tutorials.git
cd hue
make apps
sudo cp desktop/libs/hadoop/java-lib/hue-plugins-2.1.0-SNAPSHOT.jar /usr/lib/hadoop/lib/hue-plugins-2.1.0-SNAPSHOT.jar
