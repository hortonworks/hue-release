DEFAULT_EXPORT_REQUEST = dict(done_step = 0,
    db = None,
    table = None,
    columns = None,
    table_meta = None,
    confirm_recreation = None,
    recreation = False,
    operation = "replace",
    state_id = None)

import logging
LOG = logging.getLogger(__name__)
def create_export_request(session, id):
  """
  Get ExportRequest from session for query result specified by id.
  Return None if the export request does not exist.
  """

  LOG.info("create_export_request")
  data = session.get("export", None)
  LOG.info(id)
  if data is None or id not in data:
    req = ExportRequest(DEFAULT_EXPORT_REQUEST)
  else:
    req = ExportRequest(data[id])
  return req

def persist_export_request(session, id, req):
  """ 
  Persist ExportRequest into session
  """
  if "export" not in session: 
    session["export"] = { id: req }
  else:
    data = session["export"]
    data.update( {id: req} )
    session["export"] = data

class ExportRequest:

  def __init__(self, data):
    self.__dict__ = data

  def data(self):
    return self.__dict__

  @property
  def existing_table(self):
    meta = self.__dict__["table_meta"] 
    return meta and len(meta) > 0

  @property
  def new_table(self):
    return not self.existing_table
