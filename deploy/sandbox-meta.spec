Summary: Hortonworks Sandbox Metapackage
Name: sandbox-meta
Version: 1.2.1
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Vendor: Hortonworks <UNKNOWN>

Requires: sandbox-tutorials sandbox

%description
Hortonworks Sandbox Metapackage

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

chkconfig iptables off
iptables -F

chkconfig cups on

chkconfig httpd on
service httpd start

ln -s /home/sandbox/start_scripts/startup_script /etc/init.d/startup_script
chkconfig --add startup_script
chkconfig --levels 3 startup_script on



%postun
