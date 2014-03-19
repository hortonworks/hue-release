cd /usr/lib/ambari-server/web/javascripts
rm -f app.js
gunzip app.js.gz
sed -i "s/App.singleNodeInstall = false;/App.singleNodeInstall = true;/" app.js
gzip app.js
