echo id,text >>/tmp/mydata.csv;
echo 1,Hello >>/tmp/mydata.csv;
echo 2,HDP >>/tmp/mydata.csv;
echo 3,and >>/tmp/mydata.csv;
echo 4,Solr >>/tmp/mydata.csv;

su - hdfs -c "hadoop fs -mkdir -p /user/solr/data/csv"
su - hdfs -c "hadoop fs -chown solr /user/solr"
su - hdfs -c "hadoop fs -put -f /tmp/mydata.csv /user/solr/data/csv"

chown solr:solr -R /opt/solr
su - solr << EOF
cd /opt/solr

[ -e solr ] || ln -sf solr-4.10.4 solr

cd solr
cp -r example hdp
rm -fr hdp/examle* hdp/multicore
mv hdp/solr/collection1 hdp/solr/hdp1
rm hdp/solr/hdp1/core.properties
EOF
