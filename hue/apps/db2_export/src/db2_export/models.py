
from django.db import models

from enum import Enum

from beeswax.models import HiveServerQueryHistory


class ExportState(models.Model):

  STATE = Enum('submitted', 'running',
               'success',  # all rows are loaded
               'failed',   # ecounter errors during feeding or loading
               'partial',  # all data is sent to loader, but there are rows rejected
               'exceeded'  # exceeded the size limit
               )

  query_history = models.ForeignKey(HiveServerQueryHistory)
  user = models.CharField(max_length=128, db_index=True)
  schema = models.CharField(max_length=128)
  table = models.CharField(max_length=128, db_index=True)
  size = models.IntegerField(default=-1)
  finished_size = models.IntegerField(default=0)
  finished_rows = models.IntegerField(default=0)
  comitted_rows = models.IntegerField(default=0)
  last_state = models.IntegerField(default=STATE.submitted.index, db_index=True)
  create_at = models.DateTimeField(auto_now_add=True)
  update_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-create_at']

  def set_state(self, name):
    state = getattr(self.STATE, name)
    self.last_state = state.index

  def is_submitted(self):
    return self.last_state == self.STATE.submitted.index

  def is_running(self):
    return self.last_state == self.STATE.running.index

  def is_done(self):
    return self.last_state in (self.STATE.success.index,
                               self.STATE.failed.index,
                               self.STATE.partial.index,
                               self.STATE.exceeded.index)

  def is_success(self):
    return self.last_state == self.STATE.success.index

  @property
  def name(self):
    return self.STATE[self.last_state].key
