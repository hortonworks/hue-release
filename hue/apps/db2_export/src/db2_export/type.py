import re

def get_type_converter(col_ref):
  return DB2TypeConverter(col_ref)

class DB2TypeConverter:

  TYPE_MAP = {
      'tinyint':  'smallint',
      'smallint': 'smallint',
      'int':      'int',
      'bigint':   'bigint',
      'boolean':  'smallint',
      'float':    'float',
      'double':   'double',
      'string':   'varchar(200)'
  }

  RES = {
      "like_date": [ re.compile(r"date", re.IGNORECASE)]
  }

  def __init__(self, col_ref={}):
    """
    col_ref is a dict mapping column name to data type
    """
    self._col_ref = col_ref

  def convert(self, column_name, hive_type):
    ht = hive_type.lower()
    if ht not in DB2TypeConverter.TYPE_MAP:
      raise ValueError("%s is not a valid Hive type" % hive_type)
    if ht == "string" and self._search("like_date", column_name):
      db_type = "date"
    else:
      db_type = DB2TypeConverter.TYPE_MAP[ht] 

    return db_type

  def _search(self, key, column_name):
    for regex in self.RES[key]:
      if regex.search(column_name):
        return True
    return False
