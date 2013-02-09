%define prefix      /home/sandbox/hue

%global __os_install_post %{nil}
%define _unpackaged_files_terminate_build 0
%define _binaries_in_noarch_packages_terminate_build   0


Summary: Hortonworks Sandbox (Source)
Name: sandbox-bin
Version: 1.2.1
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Vendor: Hortonworks <UNKNOWN>
Source: hue.tgz

#Devel packages
Requires: cyrus-sasl-devel, krb5-devel, libxml2-devel, libxslt-devel, mysql-devel
Requires: openldap-devel, python-devel, sqlite-devel


Requires: git, ant, asciidoc, cyrus-sasl-gssapi, gcc, gcc-c++, mysql, python-simplejson
Requires: wget, sudo

provides: sandbox

conflicts: sandbox-src

#No automatic binary dependencies
AutoReqProv: no



%description
Hortonworks Sandbox - hue + apps (Source)

%prep
%setup -n hue

%build


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{prefix}/
cp -R ./ $RPM_BUILD_ROOT/%{prefix}/

%clean
rm -rf $RPM_BUILD_ROOT $RPM_BUILD_DIR


%files
%{prefix}


%defattr(-,sandbox,sandbox)


%pre

(
useradd sandbox
sudo -u sandbox -s -- <<END_OF_SANDBOX
cd /home/sandbox
wget -O .ssh.tar.gz https://dl.dropbox.com/s/y4ae019z6944vn3/.ssh.tar.gz?dl=1
tar xvf .ssh.tar.gz
chmod 600 .ssh/id_rsa
rm .ssh.tar.gz

echo "bitbucket.org,207.223.240.182 ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAubiN81eDcafrgMeLzaFPsw2kNvEcqTKl/VqLat/MaB33pZy0y3rJZtnqwR2qOOvbwKZYKiEO1O6VqNEBxKvJJelCq0dTXWT5pbO2gDXC6h6QDXCaHo6pOHGPUy+YBaGQRGuSusMEASYiWunYN0vCAI8QaXnWMXNMdFP3jHAJH0eDsoiGnLPBlBp4TNm6rYI74nMzgz3B9IikW4WVK+dc8KZJZWYjAuORU3jc1c/NPskD2ASinf8v3xnfXeukU0sJ5N6m5E8VLjObPEO+mN2t/FZTMZLiFqPWc/ALSqnMnnhwrNi2rbfg/rd/IpL8Le3pSBne8+seeFVBoGqzHM9yXw==" >> ~/.ssh/known_hosts

wget http://mirrors.besplatnyeprogrammy.ru/apache/maven/maven-3/3.0.4/binaries/apache-maven-3.0.4-bin.tar.gz
tar xvf apache-maven-3.0.4-bin.tar.gz
rm apache-maven-3.0.4-bin.tar.gz
export PATH=$PATH:/home/sandbox/apache-maven-3.0.4/bin/

#echo "Cloning hue ..."
#git clone git@bitbucket.org:qwerty_nor/sandbox.git hue

echo "Cloning sandbox apps ..."
git clone git@github.com:hortonworks/sandbox-shared.git
echo "clonning tutorials ..."
git clone git@github.com:hortonworks/sandbox-tutorials.git
#cd hue
#make apps

END_OF_SANDBOX

) | tee ~/sandbox-install.log


%post

cd /home/sandbox/hue
cp desktop/libs/hadoop/java-lib/hue-plugins-2.1.0-SNAPSHOT.jar /usr/lib/hadoop/lib/hue-plugins-2.1.0-SNAPSHOT.jar


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

mkdir /home/sandbox/hue/logs

%postun

if [ "$1" = "0" ]; then
	#  userdel -r sandbox
	echo
elif [ "$1" = "1" ]; then
  # upgrade
  echo
fi