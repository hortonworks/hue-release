from desktop.lib.conf import Config

TEMPLETON_URL = Config(
  key="templeton_url",
  help="URL of Templeton(WebHcat) server",
  default="http://localhost:50111/templeton/v1/"
)