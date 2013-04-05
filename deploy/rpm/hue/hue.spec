%global __os_install_post %{nil}
%define _unpackaged_files_terminate_build 1
%define _binaries_in_noarch_packages_terminate_build   0


Summary: Hue
Name: hue
Version: 1.2.1
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Source: hue.tgz
Source1: start_scripts.tgz
Source2: .ssh.tar.gz
#Source3: apache-maven-3.0.4-bin.tar.gz


Requires: wget, sudo, supervisor, libxslt, python-lxml

provides: hue

#No automatic binary dependencies
AutoReqProv: no



%description
Hue

%prep
%setup -n hue
%setup -b 1 -T -D -n start_scripts
%setup -b 2 -T -D -n .ssh
#%setup -b 3 -T -D -n apache-maven-3.0.4

%build


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/lib/hue/
mkdir -p $RPM_BUILD_ROOT/var/lib/hue/
mkdir -p $RPM_BUILD_ROOT/home/sandbox/.ssh

cd $RPM_BUILD_DIR/hue
cp -R ./ $RPM_BUILD_ROOT/usr/lib/hue/

cd $RPM_BUILD_DIR/start_scripts
cp -R ./ $RPM_BUILD_ROOT/usr/lib/hue/tools/start_scripts
mv $RPM_BUILD_ROOT/usr/lib/hue/tools/start_scripts/functions $RPM_BUILD_ROOT/usr/lib/hue/tools/

cd $RPM_BUILD_DIR/.ssh
cp -R ./ $RPM_BUILD_ROOT/home/sandbox/.ssh


%clean
rm -rf $RPM_BUILD_ROOT $RPM_BUILD_DIR


%files

%defattr(-,sandbox,sandbox)
/usr/lib/hue
%exclude  /usr/lib/hue/tools/start_scripts

%dir /var/lib/hue

%defattr(600,sandbox,sandbox)
/home/sandbox/.ssh

%defattr(755,sandbox,sandbox)
/usr/lib/hue/tools/start_scripts

#%config /usr/lib/hue/desktop/desktop.db


%pre

(
groupadd -f hadoop
[[ -z `cat /etc/passwd | grep sandbox` ]] && useradd -G hadoop sandbox || usermod -a -G hadoop sandbox
sudo -u sandbox -s -- <<END_OF_SANDBOX
cd /usr/lib

END_OF_SANDBOX

) | tee ~/sandbox-install.log


%post

(
sudo -u sandbox mkdir /usr/lib/hue/logs

cd /usr/lib/hue
mv desktop/libs/hadoop/java-lib/hue-plugins-*.jar /usr/lib/hadoop/lib/

ln -sf /usr/lib/hue/tools/start_scripts/ambari /etc/init.d/ambari
chkconfig --add ambari
chkconfig ambari off

ln -sf /usr/lib/hue/tools/start_scripts/startup_script /etc/init.d/startup_script
chkconfig --add startup_script
chkconfig --levels 3 startup_script on

ln -sf /usr/lib/hue/tools/start_scripts/hue /etc/init.d/hue
chkconfig --add hue
chkconfig --levels 3 hue on

#echo "Update lxml"
#source build/env/bin/activate
#pip install lxml --upgrade


mkdir /etc/hue
mv /usr/lib/hue/desktop/conf /etc/hue/
ln -s /etc/hue/conf /usr/lib/hue/desktop/


) | tee ~/sandbox-install.log

%postun

if [ "$1" = "0" ]; then
	#  userdel -r sandbox
    echo
elif [ "$1" = "1" ]; then
  # upgrade
  echo
fi
