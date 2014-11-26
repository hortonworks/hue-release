#!/bin/bash

#
# Try to do 'select * from xademo.call_detail_records' as each group user
#

hsql="select_cdr.hsql"


for group in legal network it mktg 
do
	u=${group}1
	echo "+ Running Query [`cat ${hsql}`] using user: ${u} ..."
	cat ${hsql} | ./run.sh ${u}
done
