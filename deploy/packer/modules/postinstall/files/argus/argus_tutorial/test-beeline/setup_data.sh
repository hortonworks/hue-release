my_dir=`dirname $0`

$my_dir/run.sh < $my_dir/create_table.hsql

cp $my_dir/data/* /tmp
$my_dir/run.sh < $my_dir/load_data.hsql
