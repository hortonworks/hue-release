"""
Hive QL preparation
"""

import re

PATTERNS = [
  r'^SELECT\s+.+FROM\s+([\w\.].+)\s+WHERE\s+(.+)GROUP\s+BY.+',
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+WHERE\s+(.+)ORDER\s+BY.+',
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+WHERE\s+(.+)LIMIT\s+.+',
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+WHERE\s+(.+)',
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+GROUP\s+BY.+',
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+ORDER\s+BY.+',
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+LIMIT\s+.+',
  r'^SELECT\s+.+FROM\s+([\w\.]+)'
]

PATTERN_WHERE = [
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+WHERE\s+(.+)GROUP\s+BY.+',
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+WHERE\s+(.+)ORDER\s+BY.+',
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+WHERE\s+(.+)LIMIT\s+.+',
  r'^SELECT\s+.+FROM\s+([\w\.]+)\s+WHERE\s+(.+)'
]

PATTERN_DB = r'USE\s+(\w+)'

def clean(query_str):
  return query_str.replace(r'\n', ' ').replace('`', '').replace("  ", " ").strip()

def get_dbname(query_str):
  pattern = re.compile(PATTERN_DB, re.I)
  m = re.match(pattern, query_str)
  if m:
    return m.group(1)
  return "default"

def get_select(query_str):
  """ get select clouse inside """
  for regex_pattern in PATTERNS:
    pattern = re.compile(regex_pattern, re.I)
    for m in re.finditer(pattern,query_str):
      return m.group(0)
  return ''

def get_table(query_str, dbname='default'):
  # discard sub-queries
  if query_str.upper().find('SELECT', 1) > -1:
    return ('', '')
  # discard query with join
  if 'JOIN' in query_str.upper():
    return ('', '')
  table = ''
  alias = ''
  for regex_pattern in PATTERNS:
    pattern = re.compile(regex_pattern, re.I)
    m = re.match(pattern, clean(query_str))
    if m:
      identifier = m.group(1)
      dbname_specified = '.' in identifier
      tokens = re.split(r'\.|\s+', identifier)
      if '' in tokens: tokens.remove('')

      if len(tokens) == 1:
        table = tokens[0]
      elif len(tokens) == 2:
        if dbname_specified:
          dbname, table = tokens
        else:
          table, alias = tokens
      elif len(tokens) == 3:
        dbname, table, alias = tokens
  return (dbname, table)

def get_where(query_str):
  for regex_pattern in PATTERN_WHERE:
    pattern = re.compile(regex_pattern, re.I)
    m = re.match(pattern, query_str)
    if m:
      return m.group(2).strip()
  return ''