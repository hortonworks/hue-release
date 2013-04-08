%define prefix      /usr/lib/tutorials
%global __os_install_post %{nil}
%define _unpackaged_files_terminate_build 1
%define _binaries_in_noarch_packages_terminate_build   0

Summary: Hue Tutorials
Name: hue-tutorials
Version: 1.2.1
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Source: tutorials.tgz
Source1: tutorials-env.tgz
AutoReqProv: no


provides: hue-tutorials

requires: python >= 2.6, httpd, git
requires: hue

%description
Hue Tutorials

%prep
%setup -n tutorials
gzip -dc $BB/rpm/SOURCES/tutorials-env.tgz | tar -xvvf -


%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{prefix}/

cd $RPM_BUILD_DIR/tutorials
cp -R ./ $RPM_BUILD_ROOT/%{prefix}/

%clean
rm -rf $RPM_BUILD_ROOT $RPM_BUILD_DIR

%files

%defattr(-,sandbox,sandbox)
%{prefix}


%pre

rm -f %{prefix}/tutorials_app/db/lessons.db

mkdir -p /usr/lib/tutorials
chown -R sandbox:sandbox /usr/lib/tutorials

sudo -u sandbox -s -- <<END_OF_SANDBOX

echo '{"user":"sandbox", "pass":"1111"}' > /var/lib/hue/single_user_mode
echo '{"user":"sandbox", "pass":"1111"}' > /var/lib/hue/show_credentials

cd /usr/lib/tutorials/
echo "clonning tutorials ..."
git clone git@github.com:hortonworks/sandbox-tutorials.git

mkdir -p /usr/lib/hue/logs

END_OF_SANDBOX

%post

sudo -u sandbox bash %{prefix}/tutorials_app/run/run.sh



#Proxy to 8888 port
HTTPD_CONF=/etc/httpd/conf/httpd.conf

if [ `<$HTTPD_CONF grep "Proxy to tutorials"` ]; then
    echo "Already configured httpd"
else

  cat << EOF >>$HTTPD_CONF

# Proxy to tutorials
ProxyPass /ganglia !
ProxyPass /nagios !
ProxyPass /ambarinagios !
ProxyPass /cgi-bin !
ProxyPass / http://127.0.0.1:8888/
ProxyPassReverse / http://127.0.0.1:8888/
EOF

fi


TUTORIALS="/usr/lib/tutorials"
HUE="/usr/lib/hue"

ln -s $TUTORIALS/hue_common_header.js \
            $HUE/desktop/core/static/js/hue_common_header.js


# Common header patch
cat << EOF > /tmp/common_header.mako.patch
99a100
>   <script src="/static/js/hue_common_header.js"></script>
117a120
>       handleAutoLogin();
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

ln -sf /usr/lib/hue/tools/start_scripts/tutorials /etc/init.d/tutorials
chkconfig --add tutorials
chkconfig tutorials on

chkconfig httpd on
service httpd start


%postun

if [ "$1" = "0" ]; then
  rm -rf %{prefix}
elif [ "$1" = "1" ]; then
  # upgrade
  echo
fi
