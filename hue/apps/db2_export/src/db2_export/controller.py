from db2_export import step_info
from beeswax.server.hive_server2_lib import HiveServerTColumnDesc
from celery.result import AsyncResult

import logging
LOG = logging.getLogger(__name__)


def handle_export_request(helper, request, result):
  """
  Handle export query result
  """
  LOG.info("inside handle_export_request")
  exp_req = helper.create_export_request(request.session, result.id())
  handler = StepHandler(helper, exp_req)
  LOG.info(exp_req)
  return handle_export_step(helper, handler, exp_req, request, result)

def handle_export_step(helper, handler, exp_req, request, result):
  id = result.id()

  si = helper.create_step_info(request)

  params = None
  nav_to_target = True
  if request.method == 'POST':
    wizard = helper.create_export_wizard(exp_req.existing_table,
          si.submit, exp_req.done_step)
    step = wizard.step()
    params = handler.handle_submit(step.name, request, result)
    nav_to_target = can_nav_to_target_step(params, si, step)
    if nav_to_target:
      wizard.next_step(si.target)
  else:
    wizard = helper.create_export_wizard()
  
  exp_req.done_step = wizard.done_step_index()
  helper.persist_export_request(request.session, id, exp_req.data())

  step = wizard.step()
  common = dict(query_id=id, query=result.query(), wizard=wizard)
  if nav_to_target:
    params = handler.handle_display(step.name, request, result)
  params.update(common)

  return (step.template, params)

def can_nav_to_target_step(params, si, step):
  return params is None \
      or ((si.target is not None) and si.target < si.submit \
      and step.skip_backward_validation)

class StepHandler:

  def __init__(self, helper, exp_req):
    self._helper = helper
    self._req = exp_req

    self._db = helper.create_export_db()
  
  def handle_submit(self, method, request, result):
    """
    Return a dictionary of forms with validation issues.
    """
    return getattr(self, "handle_submit_" + method)(request, result)

  def handle_submit_def_table(self, request, result):
    """
    Handle the post request for def_table
    """
    db = self._helper.create_export_db()
    db_form = self._helper.create_db_form(data=request.POST, db=db)
    if db_form.is_valid():
      self._req.db = db_form.cleaned_data
    else:
      db = None

    table_form = self._helper.create_table_form(data=request.POST, db=db)
    if table_form.is_valid():
      if db:
        t = table_form.cleaned_data
        self._req.table = t
        self._req.table_meta = db.columns(t["schema"], t["table"])
        if self._req.columns is None:
          self._req.columns = self._get_columns(result)
        return

    return dict(db=db_form, table=table_form)

  def _get_columns(self, result):
    """
    Convert query result meta data into columns(name, type, length)
    """
    result_columns = self._get_result_columns(result)
    converter = self._helper.create_type_converter({})
    for column in result_columns:
      column["db_type"] = converter.convert(column["name"], column["hive_type"])
    return result_columns

  def _get_result_columns(self, result):
    """
    return a dict with column name and type of the hive query result
    """
    data = []
    for col in result.metadata().schema.columns:
      t_col_desc = HiveServerTColumnDesc(col)
      data.append({ 'name': t_col_desc.name, 'hive_type': t_col_desc.hive_type})
    return data

  def handle_submit_def_columns(self, request, result):
    column_form = self._helper.create_column_form(data=request.POST, auto_id=None)
    if not column_form.is_valid():
      return dict(columns=column_form)

    r = self._req
    r.columns = []
    for f in column_form.forms:
      r.columns.append(f.cleaned_data)

    if r.existing_table:
      r.recreation = not self._helper.schema_matches(r.columns, r.table_meta)

  def handle_submit_confirm(self, request, result):
    data = request.POST
    if self._req.recreation:
      confirm_form = self._helper.create_confirm_recreation_form(data=data)
      if confirm_form.is_valid():
        self._req.confirm_recreation = confirm_form.cleaned_data["confirm_recreation"]
      else:
        self._req.confirm_recreation = data.get("confirm_recreation", None)
        return self._confirm_params(confirm_form)
    else:
      confirm_form = self._helper.create_confirm_operation_form(data=data)
      if confirm_form.is_valid():
        self._req.operation = confirm_form.cleaned_data["operation"]
      else:
        self._req.operation = data.get("operation", "replace")
        return self._confirm_params(confirm_form)

  def _confirm_params(self, confirm_form):
      return dict(recreation=self._req.recreation,
          table=self._get_target_table(),
          confirm=confirm_form)

  def handle_submit_export(self, request, result):
    return None

  def handle_display(self, method, request, result):
    """
    Return a dictionary of forms using the specified method
    """
    LOG.info("handle_display" + method)
    return getattr(self, "handle_display_" + method)(request, result)

  def handle_display_def_table(self, request, result):
    db_form = self._helper.create_db_form(data=self._req.db)
    table_form = self._helper.create_table_form(data=self._req.table)

    return dict(db=db_form, table=table_form)

  def handle_display_def_columns(self, request, result):
    columns_form = self._helper.create_column_form(initial=self._req.columns, auto_id=None)

    return dict(columns=columns_form)

  def handle_display_confirm(self, request, result):
    if self._req.recreation:
      confirm_form = self._helper.create_confirm_recreation_form(
          data=dict(confirm_recreation=self._req.confirm_recreation))
    else:
      confirm_form = self._helper.create_confirm_operation_form(
          data=dict(operation=self._req.operation))

    return dict(recreation=self._req.recreation,
        table=self._get_target_table(),
        confirm=confirm_form)

  def handle_display_export(self, request, result):
    do_export = True
    LOG.info(self._req.state_id)
    if self._req.state_id:
      LOG.info("Inside handle display export")
      state = self._helper.get_export_state(self._req.state_id)
      LOG.info(state.last_state)
      if not state.is_done():
        do_export = False
    limit=self._helper.get_export_limit()
    if do_export:
      self._helper.prepare_db_table(self._db, self._req)
      state = self._helper.new_export_state(self._req, result)
      LOG.info(state)
      state.save()
      self._req.state_id = state.id
      self._req.fs_ref = request.fs_ref
#     TODO: how to cancel this task
      task = self._helper.submit_export_task(self._req, limit)
      LOG.info(task.task_id)
      LOG.info(AsyncResult(task.task_id).state)
      
    return dict(req=self._req, state=state,
        table=self._get_target_table(),
        limit=limit)

  def _get_target_table(self):
    return dict(name="%s.%s" % (self._req.table["schema"], 
      self._req.table["table"]), db=self._req.db["database"])
