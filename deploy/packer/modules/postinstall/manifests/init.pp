class postinstall {

    #
    #include accumulo
  if $role=='ambari'{
    include knox
    include spark
    include hue
    include kafka
    include solr
    # include xasecure
  }

  if $sandbox=='true'{
    include sandbox
  }
  
}
