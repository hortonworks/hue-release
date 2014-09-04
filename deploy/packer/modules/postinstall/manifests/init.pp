class postinstall {

    #
    #include accumulo
  if $role=='ambari'{
    include knox
    include spark
    include hue
    include kafka
  }

  if $sandbox=='true'{
    include sandbox
  }

}
