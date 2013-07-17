import happybase
from desktop.lib.conf import Config


HBASE_HOST = Config(
  key="hbase_host",
  help="Host of Hbase Thrift2 server",
  default="localhost"
)

HBASE_PORT = Config(
  key="hbase_port",
  help="Port of Hbase Thrift2 server",
  default=9090,
  type=int
)

def config_validator():
  """
  config_validator() -> [ (config_variable, error_message) ]

  Called by core check_config() view.
  """
  try:
    connection = happybase.Connection(HBASE_HOST.get(), HBASE_PORT.get())
  except Exception, ex:
    return [(HBASE_HOST, ex.message), (HBASE_PORT, ex.message)]
  else:
    return []
