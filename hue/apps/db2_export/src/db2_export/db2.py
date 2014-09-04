from db2_export.db import ExportDB
try:
  import ibm_db_dbi
  import ibm_db
except ImportError:
  pass
from db2_export.utils import db2_create_table
from desktop.lib.django_util import PopupException

class DB2(ExportDB):

  SCHEMA_Q = "select schemaname from syscat.schemata where schemaname=?"
  TSPACE_Q = "select tbspace from syscat.tablespaces where tbspace=?"
  TABLE_Q = "select tabname from syscat.tables where tabschema=? and tabname=?"

  def _connect(self, dsn, user, password):
    self.conn = ibm_db_dbi.connect(dsn, user, password)

  def has_schema(self, schema_name):
    c =  self._cursor()
    c.execute(self.SCHEMA_Q, (schema_name.upper(),))
    return c.fetchone() is not None

  def has_table(self, schema_name, table_name):
    c =  self._cursor()
    c.execute(self.TABLE_Q, (schema_name.upper(),table_name.upper()))
    return c.fetchone() is not None

  def has_tablespace(self, tablespace_name):
    c =  self._cursor()
    c.execute(self.TSPACE_Q, (tablespace_name.upper(),))
    return c.fetchone() is not None

  def columns(self, schema_name, table_name):
    """
    return columns
    """
    # save the current schema. 
    # ibm_db seems have a bug in columns(). When you set the current schema
    # to a different schema than schema_name, the method returns empty.
    curr_schema = self.conn.get_current_schema()

    self.conn.set_current_schema(schema_name)
    # extract information
    columns = [ dict(name=col["COLUMN_NAME"], type=col["TYPE_NAME"], size=col["COLUMN_SIZE"]) for col in self.conn.columns(schema_name, table_name)] 
    # restore the current schema
    self.conn.set_current_schema(curr_schema)
    return columns

  def drop_table(self, schema_name, table_name):
    c =  self._cursor()
    try:
      c.execute("DROP TABLE %s.%s" % (schema_name, table_name))
    except Exception as e:
      err_msg = str(e)
      raise PopupException(err_msg, title="DB2 Error")

  def create_table(self, schema, table, columns, tablespace=None):
    c = self._cursor()
    try:
      c.execute(db2_create_table(schema, table, columns, tablespace))
    except Exception as e:
      raise PopupException(str(e), title="DB2 Client Error")
