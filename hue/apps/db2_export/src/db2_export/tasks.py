import logging

import celery
from celery.registry import tasks

from desktop.lib import fsmanager

from db2_export import task_helper
from beeswax import query_result

LOG = logging.getLogger(__name__)


class ExportLoad(celery.task.Task):
  #  abstract = True
    default_retry_delay = 30
    max_retries = 3

    def __call__(self, *args, **kwargs):
      return self.run(*args, **kwargs)

    def run(self, req, limit, **kwargs):
        self.req = req
        self.limit = limit
        try:
          # WORKAROUND to have ExportState object created in DB
          import time
          time.sleep(5)
          # WORKAROUND END
          state = task_helper.get_export_state(req.state_id)
          result = query_result.create(state.query_history, get_filesys(req.fs_ref))
          exporter = task_helper.create_exporter(req, state, result, limit)
          exporter.export()
        except Exception, e:
          raise e

tasks.register(ExportLoad)


def get_filesys(fs_ref):
  if fs_ref is None:
    fs_ref, fs = fsmanager.get_default_hdfs()
  else:
    try:
      fs = fsmanager.get_filesystem(fs_ref)
    except KeyError:
      raise KeyError('Cannot find filesystem called "%s"' % (fs_ref,))
  return fs
