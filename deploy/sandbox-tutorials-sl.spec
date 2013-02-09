%define shared      /home/sandbox/sandbox-shared
%define origin      %{shared}/tutorials
%define prefix      /home/sandbox/tutorials

Summary: Hortonworks Sandbox Tutorials (Symlinks)
Name: sandbox-tutorials-sl
Version: 2
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Vendor: Hortonworks <UNKNOWN>

requires: python >= 2.6, python-setuptools, python-pip, python-virtualenv, supervisor, httpd
requires: sandbox
conflicts: sandbox-tutorials-files

provides: sandbox-tutorials

%description
Sandbox Tutorials (creates symlink from sandbox-shared)

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/`dirname %{prefix}`
ln -s %{origin} $RPM_BUILD_ROOT/%{prefix}
ln -s %{shared}/start_scripts $RPM_BUILD_ROOT/home/sandbox/start_scripts

%clean
rm -rf $RPM_BUILD_ROOT $RPM_BUILD_DIR

%files
%{prefix}
/home/sandbox/start_scripts


%defattr(-,sandbox,sandbox)
%{prefix}


%pre

rm -f %{prefix}/tutorials_app/db/lessons.db

%post

bash %{shared}/deploy/tutorials-post-install.sh %{prefix}



%postun

if [ "$1" = "0" ]; then
  rm -rf %{prefix}
  rm -rf /home/sandbox/start_scripts
elif [ "$1" = "1" ]; then
  # upgrade
  echo
fi