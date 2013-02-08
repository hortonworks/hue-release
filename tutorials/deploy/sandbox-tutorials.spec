%define prefix      /home/sandbox/tutorials

Summary: Sandbox Tutorials
Name: sandbox-tutorials
Version: 2
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Vendor: Hortonworks <UNKNOWN>
Source: sandbox-tutorials-2.tgz

requires: python >= 2.6, python-setuptools, python-pip, python-virtualenv, supervisor

%description
Sandbox Tutorials

%prep
%setup

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
%{prefix}/*



%post

bash %{prefix}/deploy/tutorials-post-install.sh %{prefix}



%postun
rm -rf %{prefix}