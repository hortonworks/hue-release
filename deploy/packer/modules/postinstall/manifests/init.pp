class postinstall {

    #
    #include accumulo
  if $role=='ambari'{
    include knox
    include spark
    include hue
  }

  if $sandbox=='true'{
    include sandbox
  }
  
}
