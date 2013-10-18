%define tutorials_dir      /usr/lib/tutorials
%define hue_dir            /usr/lib/hue
%define user               hue
%define group              hadoop
%global __os_install_post %{nil}
%define  debug_package %{nil}
%define _unpackaged_files_terminate_build 1
%define _binaries_in_noarch_packages_terminate_build   0

Summary: Hue Tutorials
Name: hue-tutorials
Version: 1.2.1
Release: 3
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Source: tutorials.tgz
Source1: tutorials-env.tgz
Source2: start_scripts.tgz
Source3: .ssh.tar.gz
AutoReqProv: no


provides: hue-tutorials

requires: python >= 2.6, httpd, git
requires: hue-sandbox


%description
Hue Tutorials

%prep
%setup -n tutorials
gzip -dc $BB/rpm/SOURCES/tutorials-env.tgz | tar -xvvf -
%setup -b 2 -T -D -n start_scripts
%setup -b 3 -T -D -n .ssh

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{tutorials_dir}/
mkdir -p $RPM_BUILD_ROOT%{hue_dir}/tools
mkdir -p $RPM_BUILD_ROOT%{hue_dir}/.ssh

cd $RPM_BUILD_DIR/tutorials
cp -R ./ $RPM_BUILD_ROOT%{tutorials_dir}/

cd $RPM_BUILD_DIR/start_scripts
cp -R ./ $RPM_BUILD_ROOT%{hue_dir}/tools/start_scripts/
mv $RPM_BUILD_ROOT%{hue_dir}/tools/start_scripts/functions $RPM_BUILD_ROOT%{hue_dir}/tools/

cd $RPM_BUILD_DIR/.ssh
cp -R ./ $RPM_BUILD_ROOT%{hue_dir}/.ssh/



%clean
rm -rf $RPM_BUILD_ROOT $RPM_BUILD_DIR

%files

%defattr(-,%{user},%{group})
%{tutorials_dir}


%pre

rm -f %{tutorials_dir}/tutorials_app/db/lessons.db

mkdir -p %{tutorials_dir}
chown -R %{user}:%{group} %{tutorials_dir}

sudo -u %{user} -s -- <<END_OF_SANDBOX

echo '{"user":"hue", "pass":"1111"}' > /var/lib/hue/single_user_mode
echo '{"user":"hue", "pass":"1111"}' > /var/lib/hue/show_credentials

cd %{tutorials_dir}
echo "clonning tutorials ..."
[ ! -d sandbox-tutorials ] && git clone git@github.com:hortonworks/sandbox-tutorials.git
cd sandbox-tutorials
git reset --hard HEAD && git pull origin master

mkdir -p %{hue_dir}/logs

END_OF_SANDBOX

%post

rm -f %{tutorials_dir}/tutorials_app/db/db_version.txt
sudo -u %{user} bash %{tutorials_dir}/tutorials_app/run/run.sh


TUTORIALS="%{tutorials_dir}"
HUE="%{hue_dir}"

ln -s $TUTORIALS/hue_common_header.js \
            $HUE/desktop/core/static/js/hue_common_header.js


# Common header patch
cat << EOF > /tmp/common_header.mako.patch
99a100
>   <script src="/static/js/hue_common_header.js"></script>
EOF

patch $HUE/desktop/core/src/desktop/templates/common_header.mako < /tmp/common_header.mako.patch


# set hue.ini configuration
function ini_set() {
    sed -i "s/\($2 *= *\).*/\1$3/" "$1"
}

HUEINI=/etc/hue/conf/hue.ini

ini_set $HUEINI tutorials_path '\"\/usr\/lib\/tutorials\/sandbox-tutorials\"'
ini_set $HUEINI tutorials_update_script '"\/usr\/lib\/tutorials\/tutorials_app\/run\/run.sh"'
ini_set $HUEINI tutorials_installed True

ln -sf %{hue_dir}/tools/start_scripts/tutorials /etc/init.d/tutorials
chkconfig --add tutorials
chkconfig tutorials on

ln -sf %{hue_dir}/tools/start_scripts/ambari /etc/init.d/ambari
chkconfig --add ambari
chkconfig ambari off

ln -sf %{hue_dir}/tools/start_scripts/hbase-starter /etc/init.d/hbase-starter
chkconfig --add hbase-starter
chkconfig hbase-starter off

chkconfig httpd on
service httpd start


%postun

if [ "$1" = "0" ]; then
  rm -rf %{tutorials_dir}
elif [ "$1" = "1" ]; then
  # upgrade
  echo
fi





##### Start Scripts #####
%package -n hue-sandbox
Summary: Init-scripts and splash
Requires: hue, python >= 2.6

%description -n hue-sandbox
Init scripts and splash

%post -n hue-sandbox
# ln -sf %{hue_dir}/tools/start_scripts/hue /etc/init.d/hue
# chkconfig --add hue
# chkconfig --level 3 hue on

echo "Sandbox=%{sandbox_timestamp}" > /var/lib/hue/EXTRA_VERSIONS

/etc/init.d/hue setup

ln -sf /usr/lib/hue/tools/start_scripts/startup_script /etc/init.d/startup_script
chkconfig --add startup_script
chkconfig --level 3 startup_script on


%files -n hue-sandbox
%defattr(755,%{user},%{group})
%{hue_dir}
%defattr(600,%{user},%{group})
%{hue_dir}/.ssh

%preun
rm -f /var/lib/hue/EXTRA_VERSIONS
