%define origin      /home/sandbox/sandbox-shared/tutorials
%define prefix      /home/sandbox/tutorials

Summary: Hortonworks Sandbox Tutorials (Symlinks)
Name: sandbox-tutorials-sl
Version: 2
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Vendor: Hortonworks <UNKNOWN>

requires: python >= 2.6, python-setuptools, python-pip, python-virtualenv, supervisor
conflicts: sandbox-tutorials-files

provides: sandbox-tutorials

%description
Sandbox Tutorials (creates symlink from sandbox-shared)

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/`dirname %{prefix}`
ln -s %{origin} $RPM_BUILD_ROOT/%{prefix}

%clean
rm -rf $RPM_BUILD_ROOT $RPM_BUILD_DIR

%files
%{prefix}

%defattr(-,sandbox,sandbox)
%{prefix}


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