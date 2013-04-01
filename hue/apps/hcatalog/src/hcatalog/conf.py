import urllib2
from desktop.lib.conf import Config


TEMPLETON_URL = Config(
  key="templeton_url",
  help="URL of Templeton(WebHcat) server",
  default="http://localhost:50111/templeton/v1/"
)

def config_validator():
  """
  config_validator() -> [ (config_variable, error_message) ]

  Called by core check_config() view.
  """
  from pig.templeton import Templeton
  t = Templeton()
  try:
  	t.get("status")
  except urllib2.URLError, error:
    return [ (TEMPLETON_URL, "%s" % (error.reason)) ]
  else:
  	return []

