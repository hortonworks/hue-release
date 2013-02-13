%define prefix      /home/sandbox/tutorials
%global __os_install_post %{nil}
%define _unpackaged_files_terminate_build 1
%define _binaries_in_noarch_packages_terminate_build   0

Summary: Hortonworks Sandbox Tutorials
Name: sandbox-tutorials-files
Version: 2
Release: 1
License: Apache License, Version 2.0
Group: Development/Libraries
BuildArch: noarch
Vendor: Hortonworks <UNKNOWN>
Source: tutorials.tgz
Source1: tutorials-env.tgz
AutoReqProv: no


provides: sandbox-tutorials

requires: python >= 2.6, python-setuptools, python-pip, python-virtualenv, supervisor, httpd
requires: sandbox
conflicts: sandbox-tutorials-sl

%description
Sandbox Tutorials (with files)

%prep
%setup -n tutorials
gzip -dc /root/rpm/SOURCES/tutorials-env.tgz | tar -xvvf -


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
%dir %{prefix}


%pre

rm -f %{prefix}/tutorials_app/db/lessons.db

%post

sudo -u sandbox bash %{prefix}/tutorials_app/run/run.sh



if [ `</etc/supervisord.conf grep 'tutorial\]'` ]; then
    echo "Already set up in supervisord.conf"
else
    echo "Add to supervisord.conf"
    cat << EOF >>/etc/supervisord.conf
[program:hue_tutorial]
command=/home/sandbox/tutorials/.env/bin/python /home/sandbox/tutorials/manage.py  run_gunicorn 0:8888
autostart=true              ; start at supervisord start (default: true)
autorestart=true            ; retstart at unexpected quit (default: true)
user=sandbox                   ; setuid to this UNIX account to run the program
log_stderr=true             ; if true, log program stderr (def false)
logfile=/home/sandbox/tutorials/tut.log    ; child log path, use NONE for none; default AUTO

EOF

fi

#Proxy to 8888 port
LINE="ProxyPass / http://127.0.0.1:8888/"
HTTPD_CONF=/etc/httpd/conf/httpd.conf

if [ `<$HTTPD_CONF grep "Proxy to tutorials"` ]; then
    echo "Already configured httpd"
else

  cat << EOF >>$HTTPD_CONF

# Proxy to tutorials
ProxyPass /ganglia !
ProxyPass /nagios !
ProxyPass / http://127.0.0.1:8888/
ProxyPassReverse / http://127.0.0.1:8888/
EOF

fi

TUTORIALS="/home/sandbox/tutorials"
HUE="/home/sandbox/hue"

ln -s $TUTORIALS/hue_common_header.js \
            $HUE/desktop/core/static/js/hue_common_header.js


# Common header patch
cat << EOF > /tmp/common_header.mako.patch
98a99
>   <script src="/static/js/hue_common_header.js"></script>
115a117
>       handleAutoLogin();
EOF

patch $HUE/desktop/core/src/desktop/templates/common_header.mako < /tmp/common_header.mako.patch


# Single user mode patch

cat << EOF > /tmp/auth_views.py.patch
--- views.py.old	2012-11-28 16:03:17.497518739 +0200
+++ views.py	2012-11-28 16:15:25.162905369 +0200
@@ -20,7 +20,7 @@
 import django.contrib.auth.views
 from django.core import urlresolvers
 from django.core.exceptions import SuspiciousOperation
-from django.contrib.auth import login, get_backends
+from django.contrib.auth import authenticate, login, get_backends
 from django.contrib.auth.models import User
 from django.contrib.sessions.models import Session
 from django.http import HttpResponseRedirect
@@ -33,6 +33,8 @@
 
 LOG = logging.getLogger(__name__)
 
+SINGLE_USER_MODE = True
+
 
 def get_current_users():
   """Return dictionary of User objects and
@@ -69,10 +71,16 @@
   redirect_to = request.REQUEST.get('next', '/')
   login_errors = False
   is_first_login_ever = first_login_ever()
-  if request.method == 'POST':
-    form = django.contrib.auth.forms.AuthenticationForm(data=request.POST)
-    if form.is_valid():
-      login(request, form.get_user())
+  if SINGLE_USER_MODE or request.method == 'POST':
+    if not SINGLE_USER_MODE:
+      form = django.contrib.auth.forms.AuthenticationForm(data=request.POST)
+    if SINGLE_USER_MODE or form.is_valid():
+      if SINGLE_USER_MODE:
+        user = authenticate(username="sandbox", password="sandbox")  
+      else:
+        user = form.get_user()
+
+      login(request, user)
       if request.session.test_cookie_worked():
         request.session.delete_test_cookie()

EOF

patch /home/sandbox/hue/desktop/core/src/desktop/auth/views.py < /tmp/auth_views.py.patch


%postun

if [ "$1" = "0" ]; then
  rm -rf %{prefix}
elif [ "$1" = "1" ]; then
  # upgrade
  echo
fi