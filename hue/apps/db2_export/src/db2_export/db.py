class ExportDB:

  def __init__(self):
    self.conn = None
    self.cursor = None

  def is_connected(self):
    return self.conn != None

  def connect(self, spec):
    if not isinstance(spec, dict):
      raise ValueError("Connection spec should be a dict!")
    if not self.is_connected():
      self._connect(spec["database"], spec["user"], spec["password"])

  def _cursor(self):
    return self.cursor or self.conn.cursor()

  def _connect(self, dsn, user, passwd):
    raise NotImplementedError()

  def close(self):
    if self.cursor is not None:
      self.cursor.close()

    if self.conn is not None:
      self.conn.close()

  def has_schema(self, schema_name):
    raise NotImplementedError()

  def has_table(self, schema_name, table_name):
    raise NotImplementedError()

  def has_tablespace(self, tablespace_name):
    raise NotImplementedError()

  def columns(self, schema_name, table_name):
    raise NotImplementedError()
