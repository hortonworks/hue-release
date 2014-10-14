class postpostinstall{
  exec { "slider_fix":
	command => 'su hdfs -c "hdfs dfs -mkdir /user/yarn"; su hdfs -c "hdfs dfs -chown yarn:hdfs /user/yarn"',
  	logoutput => true
  }
}