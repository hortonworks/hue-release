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

requires: python >= 2.6, supervisor, httpd, git
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
%{prefix}

%defattr(-,sandbox,sandbox)
%{prefix}


%pre

rm -f %{prefix}/tutorials_app/db/lessons.db

mkdir -p /usr/lib/tutorials
chown -R sandbox:sandbox /usr/lib/tutorials

sudo -u sandbox -s -- <<END_OF_SANDBOX

cd /usr/lib/tutorials/
echo "clonning tutorials ..."
git clone git@github.com:hortonworks/sandbox-tutorials.git

mkdir -p /usr/lib/hue/logs

END_OF_SANDBOX

%post

sudo -u sandbox bash %{prefix}/tutorials_app/run/run.sh



if [ `</etc/supervisord.conf grep 'tutorial\]'` ]; then
    echo "Already set up in supervisord.conf"
else
    echo "Add to supervisord.conf"
    cat << EOF >>/etc/supervisord.conf
[program:hue_tutorial]
command=/usr/lib/tutorials/.env/bin/python /usr/lib/tutorials/manage.py  run_gunicorn 0:8888
autostart=true              ; start at supervisord start (default: true)
autorestart=true            ; retstart at unexpected quit (default: true)
user=sandbox                   ; setuid to this UNIX account to run the program
log_stderr=true             ; if true, log program stderr (def false)
logfile=/usr/lib/tutorials/tut.log    ; child log path, use NONE for none; default AUTO

EOF

fi

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


# Single user mode patch

cat << EOF > /tmp/auth_views.py.patch
23c23
< from django.contrib.auth import login, get_backends
---
> from django.contrib.auth import authenticate, login, get_backends
38a39,40
> SINGLE_USER_MODE = True
> 
75c77
<   if request.method == 'POST':
---
>   if SINGLE_USER_MODE or request.method == 'POST':
81c83,84
<       auth_form = AuthenticationForm(data=request.POST)
---
>       if not SINGLE_USER_MODE: 
>         auth_form = AuthenticationForm(data=request.POST)
83c86
<       if auth_form.is_valid():
---
>       if SINGLE_USER_MODE or auth_form.is_valid():
86c89,93
<         user = auth_form.get_user()
---
>         if not SINGLE_USER_MODE:
>           user = auth_form.get_user()
>         else:
>           user = authenticate(username="sandbox", password="1111")
> 
EOF

patch /usr/lib/hue/desktop/core/src/desktop/auth/views.py < /tmp/auth_views.py.patch

chkconfig httpd on
service httpd start

/etc/init.d/supervisord restart


%postun

if [ "$1" = "0" ]; then
  rm -rf %{prefix}
elif [ "$1" = "1" ]; then
  # upgrade
  echo
fi
