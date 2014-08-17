from db2_export.models import ExportState

def get_export_state(id):
  return ExportState.objects.get(id=id)

def new_export_state(req, result):
  t = req.table
  state = ExportState()
  state.user = req.db["user"]
  state.schema = t["schema"]
  state.table = t["table"]
  state.size = result.size()
  state.finished_size = 0L
  state.query_history = result.query_history
  return state
