from beeswax.models import QueryHistory
from beeswax.models import HiveServerQueryHistory
from desktop.lib.exceptions_renderable import PopupException
from beeswax.server.hive_server2_lib import HiveServerClientCompatible, HiveServerClient
from beeswax.server import dbms
from beeswax import query_helper
import logging
import time
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from hadoop.fs.exceptions import WebHdfsException

LOG = logging.getLogger(__name__)
_DATA_WAIT_SLEEP=0.1

def create_from_request(request, id):
  query_history = HiveServerQueryHistory.objects.get(id=id)
  handle, state = _get_query_handle_and_state(query_history)
  return QueryResult(query_history, HiveServerClientCompatible(HiveServerClient(query_history.get_query_server_config(), request.user)), request.fs, handle, state)

def create(query_history, fs):
  client = HiveServerClientCompatible(HiveServerClient(query_history.get_query_server_config(), query_history.owner))
  handle, state = _get_query_handle_and_state(query_history)
  return QueryResult(query_history, client, fs, handle, state)


def _get_query_handle_and_state(query_history):
  """
  Front-end wrapper to handle exceptions. Expects the query to be submitted.
  """
  handle = query_history.get_handle()

  if handle is None:
    raise PopupException(_("Failed to retrieve query state from the Query Server."))

  query_server = query_history.get_query_server_config()

  if query_server['server_name'] == 'impala' and not handle.has_result_set:
    state = QueryHistory.STATE.available
  else:
    state = dbms.get(query_history.owner, query_history.get_query_server_config()).get_state(handle)
  if state is None:
    msg = "Hue has just been restarted due to a query that was consuming all CPU rendering the server unresponsive.\
      This may have been a result of another user on this server. \
       Please ensure your query is using a partition filter when using a partitioned table. \
        If you are sure you are running a well-optimized query, please ignore this message. \
         Hue is now back up and queries can be submitted again."

    raise PopupException(msg, title="Hue Restarted")
  return (handle, state)


class QueryResult:

  def __init__(self, query_history, db_client, file_sys, handle, state):
    self.query_history = query_history
    self.db_client = db_client
    self.file_sys = file_sys
    self.handle = handle
    self.state = state
    self.result_metadata = None
    self.result_size = None

  def is_ready(self):
    """
    return True if the result is available
    """
    return self.state == HiveServerQueryHistory.STATE.available

  def is_failed(self):
    return self.state == HiveServerQueryHistory.STATE.failed

  def is_expired(self):
    return self.state == HiveServerQueryHistory.STATE.expired

  def owned_by(self, user):
    return self.query_history.owner == user

  def id(self):
    return self.query_history.id

  def query(self):
    return self.query_history.query

  def size(self):

    """return query result size in bytes. return -1 if the result is in a table or a partition of a table."""
    if self.result_size is None:
      self.result_size = -1
      md = self.metadata()
      ## added new check to avoid meta data query failure
      if md and md.in_tablename is None and md.table_dir:
        path = self.file_sys.urlsplit(md.table_dir)[2]
        total = 0
        ## validate local file query
        if path.split(":")[0] != 'file':
          try:
            for stats in self.file_sys.listdir_stats(path):
              total += stats['size']
            self.result_size = total
          except WebHdfsException:
            self.result_size=0
    return self.result_size

  def metadata(self):
    """
    return query result meta data
    """
    if self.result_metadata is None:
      try:
        self.result_metadata = self.db_client.get_results_metadata(self.handle)
      except Exception, e:
        LOG.info(str(e))
    return self.result_metadata


  def data_generator(self):
    """
    Return a generator object for all results.
    """
    global _DATA_WAIT_SLEEP
    is_first_row = True
    next_row = 0
    results = None

    while True:
      # Make sure that we have the next batch of ready results
      while results is None or not results.ready:
        results = self.db_client.fetch(self.handle, start_over=is_first_row)
        if not results.ready:
          time.sleep(_DATA_WAIT_SLEEP)

      if is_first_row:
        is_first_row = False

      for row in results.rows():
        yield u'\t'.join(force_unicode(e, errors='replace') for e in row)

      if results.has_more:
        results = None
      else:
        break
