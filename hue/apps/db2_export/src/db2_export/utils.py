from mako.template import Template

CREATE_TABLE_TEMPLATE = """
  create table ${schema}.${table} (
    ${columns[0]["name"]} ${columns[0]["db_type"]}
  % for column in columns[1:]:
      , ${column["name"]} ${column["db_type"]}
  % endfor
  ) ${tablespace_clause} 
"""

LOAD_SCRIPT_TEMPLATE = """#!/bin/bash
set -e
db2 connect to ${db} user ${user} using ${password}
db2 "import from ${fifo} of del modified by coldel0x09 nochardel codepage=1208 messages ${message} ${operation} into ${schema}.${table} ${columns_clause} ${stat_clause}"
db2 terminate
"""

def db2_create_table(schema, table, columns, tablespace=None):
  """
  Generate create table statement from table and columns
  """
  options = dict(schema=schema, table=table, columns=columns)
  if tablespace and len(tablespace) > 0:
    options["tablespace_clause"] = "in %s" % tablespace
  else:
    options["tablespace_clause"] = ""
    
  return Template(CREATE_TABLE_TEMPLATE).render(**options)

def db2_load_script(options):
  columns = options.get("columns", [])
  clause = ', '.join(columns)
  if len(clause) > 0: 
    options["columns_clause"] = "(%s)" % clause
  else:
    options["columns_clause"] = clause

  operation = options.get("operation", "replace")
  options["stat_clause"] = ""
  #if operation == "replace":
  #  options["stat_clause"] = "statistics use profile nonrecoverable"
  #else:
  #  options["stat_clause"] = ""

  return Template(LOAD_SCRIPT_TEMPLATE).render(**options)
