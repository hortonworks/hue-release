import happybase
from desktop.lib.exceptions import StructuredThriftTransportException
from conf import HBASE_HOST, HBASE_PORT
from thrift.transport.TTransport import TTransportException
from desktop.lib.exceptions_renderable import PopupException

client = None

def get_client():
  global client
  if client is None:
    try:
      client = HBase()
      return client
    except Exception, ex:
      raise PopupException(ex.message)
  else:
    return client


class HBase(object):

  def __init__(self):
    try:
      self.pool = happybase.ConnectionPool(size=3, host=HBASE_HOST.get(), port=HBASE_PORT.get())
    except TTransportException, ex:
      raise StructuredThriftTransportException(ex)

  def table_list(self):
    """
    List of HBase tables
    """
    with self.pool.connection() as connection:
      return connection.tables()

  def create_table(self, name, column_families):
    """
    Creates HBase table.
    :param name: table_name
    :type name: string
    :param column_families
    :type column_families: dict
      :param max_versions
      :type max_versions: int
      :param compression
      :type compression: string
      :param in_memory
      :type in_memory: bool
      :param bloom_filter_type
      :type bloom_filter_type: string
      :param bloom_filter_vector_size
      :type bloom_filter_vector_size: int
      :param bloom_filter_nb_hashes
      :type bloom_filter_nb_hashes: int
      :param block_cache_enabled
      :type block_cache_enabled: bool
      :param time_to_live
      :type time_to_live: int
    """
    with self.pool.connection() as connection:
      connection.create_table(name, column_families)


  def get_table(self, table_name, use_prefix=False):
    with self.pool.connection() as connection:
      return connection.table(table_name, use_prefix)

  def is_table_enabled(self, table):
    with self.pool.connection() as connection:
      return connection.is_table_enabled(table)

  def disable_table(self, table):
    with self.pool.connection() as connection:
      return connection.disable_table(table)

  def enable_table(self, table):
    with self.pool.connection() as connection:
      return connection.enable_table(table)

  def delete_table(self, table, disable=True):
    with self.pool.connection() as connection:
      return connection.delete_table(table, disable)

  def compact_table(self, table, major=False):
    with self.pool.connection() as connection:
      return connection.compact_table(table, major)

    