import urllib2
from desktop.lib.conf import Config


TEMPLETON_URL = Config(
  key="templeton_url",
  help="URL of Templeton(WebHcat) server",
  default="http://localhost:50111/templeton/v1/"
)

SECURITY_ENABLED = Config(
  key="security_enabled",
  help="Whether to use kerberos auth",
  default=False,
  type=bool
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
  except Exception, error:
    return [ (TEMPLETON_URL, "%s" % (error.message)) ]
  else:
  	return []

