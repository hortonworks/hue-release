class postinstall {

    #
    #include accumulo
  if $role=='ambari'{
    include knox
    include spark
    include hue
    include solr
  }

  if $sandbox=='true'{
    include sandbox
  }
  
}
