yum -y install createrepo git rpm-build ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi gcc gcc-c++ krb5-devel libxml2-devel libxslt-devel mysql  mysql-devel openldap-devel python-devel python-simplejson sqlite-devel
easy_install virtualenv
su - sandbox
cd /home/sandbox
mv hue hue_old
wget http://www.us.apache.org/dist/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz
tar xvf apache-maven-3.0.5-bin.tar.gz
rm apache-maven-3.0.5-bin.tar.gz
cd sandbox-shared/hue
PREFIX=/home/sandbox make install