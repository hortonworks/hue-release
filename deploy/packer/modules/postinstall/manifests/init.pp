class postinstall {
    #
    # class {accumulo:
    #   stage => postinstall_1
    # }
  if $role=='ambari'{
    class {knox:
      stage => postinstall_1
    }
    # class {spark:
    #   stage => postinstall_1
    # }
    class {hue:
      stage => postinstall_1
    }
    # class {kafka:
    #   stage => postinstall_1
    # }
    class {solr:
      stage => postinstall_1
    }
    class {ambari_views:
      stage => postinstall_1
    }
    # class {xasecure:
    #   stage => postinstall_1
    # }
    class {argus:
      stage => postinstall_2
    }
  }

  if $sandbox=='true'{
    class {sandbox:
      stage => postinstall_1
    }
  }
}
