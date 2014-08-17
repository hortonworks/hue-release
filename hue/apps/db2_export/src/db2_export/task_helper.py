from db2_export import state_helper
from db2_export.db2_exporter import DB2Exporter

get_export_state = state_helper.get_export_state

def create_exporter(export_request, state, result, limit):
  return DB2Exporter(export_request, state, result, limit)
