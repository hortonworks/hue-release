echo "Setup virtualenv..."
cd $1
virtualenv .env
source .env/bin/activate
pip install django==1.4 django-mako gunicorn mysql-python

echo "Updating tutorials..."
sudo -u sandbox bash $1/tutorials_app/run/run.sh

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


#Proxy to 8888 port
LINE="ProxyPass / http://127.0.0.1:8888/"
HTTPD_CONF=/etc/httpd/conf/httpd.conf
[ `<$HTTPD_CONF grep "$LINE"` ] || echo "$LINE" >> $HTTPD_CONF

fi