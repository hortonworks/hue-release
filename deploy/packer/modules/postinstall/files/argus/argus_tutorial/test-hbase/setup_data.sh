my_dir=`dirname $0`

HBASE=/usr/bin/hbase

set -x

#Create tables
$HBASE shell < $my_dir/drop-hbase.sql
$HBASE shell < $my_dir/create-hbase.sql

#Insert tables
$HBASE shell < $my_dir/insert-hbase.sql

