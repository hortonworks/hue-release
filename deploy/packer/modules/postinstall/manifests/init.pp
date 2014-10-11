class postinstall {

    #
    #include accumulo
  if $role=='ambari'{
    include knox
    #include spark
    include hue
    #include kafka
    include solr
    include ambari_views
    # include xasecure
    include argus
  }

  if $sandbox=='true'{
    include sandbox
  }
}
