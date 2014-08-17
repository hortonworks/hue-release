from beeswax.wizard import create_wizard

SPEC_TABLE   = { "name": "def_table", "title": "Table", 
    "template": "export_def_table.mako"} 
SPEC_COLUMNS = { "name": "def_columns", "title": "Columns", 
    "template": "export_def_columns.mako"} 
SPEC_EXPORT  = { "name": "export", "title": "Export",  
    "template": "export_result.mako"}
SPEC_CONFIRM = { "name": "confirm", "title": "Confirm", 
    "template": "export_confirm.mako",
    "skip_backward_validation": True }

SPECS_FOR_NEW = [ SPEC_TABLE, SPEC_COLUMNS, SPEC_EXPORT ]
SPECS_FOR_EXISTING = [ SPEC_TABLE, SPEC_COLUMNS, SPEC_CONFIRM, SPEC_EXPORT ]

def create_export_wizard(existing=False, curr_idx=None, done_idx=None):
  if existing:
    specs = SPECS_FOR_EXISTING
  else:
    specs = SPECS_FOR_NEW

  return create_wizard(specs, curr_idx, done_idx)
