from db2_export.forms import *
from db2_export.db2 import DB2
from db2_export import request, step_info, wizard, type
from beeswax import conf

#############################
# Export DB creation
def create_export_db():
  return DB2()
  
def prepare_db_table(db, req):
  if req.new_table or req.recreation: 
    db.connect(req.db)
    t = req.table
    if req.recreation \
        and db.has_table(t["schema"], t["table"]):
      db.drop_table(t["schema"], t["table"])
    db.create_table(t["schema"], t["table"], req.columns)

#############################
# Form creation
def create_db_form(**data):
  return ExportDBForm(**data)

def create_table_form(**data):
  return ExportTableForm(**data)

create_type_converter=type.get_type_converter

def create_column_form(**data):
  return ExportColumnFormSet(**data)

def create_confirm_recreation_form(**data):
  return ExportConfirmRecreationForm(**data)

def create_confirm_operation_form(**data):
  return ExportConfirmOperationForm(**data)

#############################
# Export Request
create_export_request = request.create_export_request
persist_export_request = request.persist_export_request

def schema_matches(columns, table_meta):
  #TODO: 
  return False

#############################
# Export State
from db2_export import state_helper

get_export_state = state_helper.get_export_state
new_export_state = state_helper.new_export_state

#############################
# Export Load Task
from db2_export.tasks import ExportLoad

def submit_export_task(export_request, limit):
  try:
    return ExportLoad.delay(export_request, limit)
  except Exception, e:
    raise Exception("DB2 data export is not available at this time please try after some time or contact hdphelp@expedia.com, Error: %s"%str(e))
    
#  return export_load.apply_async(args=[export_request, limit], retry=True, retry_policy={
#     'max_retries': 3,
#     'interval_start': 0,
#     'interval_step': 2,
#     'interval_max': 5,
#     }, time_limit = 60)


#############################
# StepInfo
create_step_info = step_info.create

#############################
# Wizard
create_export_wizard = wizard.create_export_wizard

#############################
# Export Limit
def get_export_limit():
  return conf.EXPORT_LIMIT.get()
