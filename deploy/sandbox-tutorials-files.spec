%define prefix      /home/sandbox/tutorials

Summary: Hortonworks Sandbox Tutorials
Name: sandbox-tutorials-files
Version: 2
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Vendor: Hortonworks <UNKNOWN>
Source: tutorials.tgz

provides: sandbox-tutorials

requires: python >= 2.6, python-setuptools, python-pip, python-virtualenv, supervisor
conflicts: sandbox-tutorials-sl

%description
Sandbox Tutorials (with files)

%prep
%setup -n tutorials

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


%pre

rm -f %{prefix}/tutorials_app/db/lessons.db

%post

bash %{prefix}/deploy/tutorials-post-install.sh %{prefix}



%postun

if [ "$1" = "0" ]; then
  rm -rf %{prefix}
elif [ "$1" = "1" ]; then
  # upgrade
fi