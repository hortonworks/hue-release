ln -s /home/sandbox/sandbox-shared/start_scripts/ /home/sandbox/start_scripts && \
      ln -s /home/sandbox/sandbox-shared/tutorials/ /home/sandbox/tutorials

yum install python-setuptools

cd /home/sandbox/tutorials && \
      easy_install pip && pip install virtualenv && virtualenv .env && \
      . .env/bin/activate && pip install django==1.4 django-mako gunicorn

cd /home/sandbox/tutorials/tutorials_app/run/ && sudo -u sandbox bash run.sh

ln -s /home/sandbox/tutorials/hue_common_header.js \
            /home/sandbox/hue/desktop/core/static/js/hue_common_header.js

echo "======================================="
echo "Add tutorials to supervisor"

echo "Add to supervisord.conf automatically? (yes/no)"
read CONF
if [ "x$CONF" = "xyes" ] ; then
    output="/etc/supervisord.conf"
else
    output="/dev/tty"
    echo "Put this into the /etc/supervisord.conf"
fi

echo
cat << EOF >>$output
[program:hue_tutorial]
command=/home/sandbox/tutorials/.env/bin/python /home/sandbox/tutorials/manage.py  run_gunicorn 0:8888
autostart=true              ; start at supervisord start (default: true)
autorestart=true            ; retstart at unexpected quit (default: true)
user=sandbox                   ; setuid to this UNIX account to run the program
log_stderr=true             ; if true, log program stderr (def false)
logfile=/home/sandbox/tutorials/tut.log    ; child log path, use NONE for none; default AUTO
EOF

echo "======================================="

read -p "Press [Enter] to $ vim /etc/supervisord.conf"
vim /etc/supervisord.conf

echo "Add support of single user mode for hue? (yes/no)"
read CONF
if [ "x$CONF" = "xyes" ] ; then
    patch /home/sandbox/hue/desktop/core/src/desktop/auth/views.py < /home/sandbox/sandbox-shared/instructions/patches/auth_views.py.patch
fi

echo 'Add "Sign in anonymously" button? (yes/no)'
read CONF
if [ "x$CONF" = "xyes" ] ; then
    patch /home/sandbox/hue/desktop/core/src/desktop/templates/login.mako < /home/sandbox/sandbox-shared/instructions/patches/login.mako.patch
fi


patch -R /home/sandbox/hue/desktop/core/src/desktop/templates/common_header.mako < /home/sandbox/sandbox-shared/instructions/patches/common_header.mako.patch
echo
echo
echo

echo 'If you need "logout" in submenu of user profile, add following lines to '\
     'common_header.mako after <a class="userProfile"... line'

cat << EOF
             <li class="divider"></li>
             <li><a href="/accounts/logout/">${_('Sign Out')}</a></li>
EOF
echo
echo

read -p "Press [Enter] to $ vim .../common_header.mako"

vim /home/sandbox/hue/desktop/core/src/desktop/templates/common_header.mako

/etc/init.d/supervisord restart
echo
echo

echo "[INFO] If you need AnonymousUser, follow tutorials_installation_manuals.txt"
echo
echo

yum install httpd
chkconfig --levels 3 httpd on

echo "Start scripts:"
echo
ln -s /home/sandbox/start_scripts/startup_script /etc/init.d/startup_script
chkconfig --add startup_script
chkconfig --levels 3 startup_script on
