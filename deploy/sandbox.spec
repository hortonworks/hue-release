Summary: Hortonworks Sandbox
Name: sandbox
Version: 1.2.1
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Vendor: Hortonworks <UNKNOWN>

Requires: git, ant, asciidoc, cyrus-sasl-devel, cyrus-sasl-gssapi, gcc, gcc-c++, krb5-devel
Requires: libxml2-devel, libxslt-devel, mysql, mysql-devel, openldap-devel, python-devel, python-simplejson
Requires: sqlite-devel


%description
Hortonworks Sandbox - hue + apps

%build


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/


%clean
rm -rf $RPM_BUILD_ROOT $RPM_BUILD_DIR


%files


%defattr(-,sandbox,sandbox)


%pre


%post

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


if [ `</etc/supervisord.conf grep 'sandbox\]'` ]; then
    echo "Already set up in supervisord.conf"
else
    echo "Add to supervisord.conf"
    cat << EOF >>/etc/supervisord.conf
[program:sandbox]
command=/home/sandbox/hue/build/env/bin/supervisor ; the program (relative uses PATH, can take args)
autostart=true              ; start at supervisord start (default: true)
autorestart=true            ; retstart at unexpected quit (default: true)
user=sandbox                 ; setuid to this UNIX account to run the program
log_stderr=true             ; if true, log program stderr (def false)
logfile=/home/sandbox/hue/logs/sandbox.log    ; child log path, use NONE for none; default AUTO
EOF

fi


%postun

if [ "$1" = "0" ]; then
  rm -rf %{prefix}
elif [ "$1" = "1" ]; then
  # upgrade
fi