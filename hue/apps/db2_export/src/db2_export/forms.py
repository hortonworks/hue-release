#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django import forms
from django.forms.formsets import formset_factory
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext as _

try:
  from ibm_db_dbi import OperationalError, ProgrammingError
except ImportError:
  pass

EXPORT_DBS=("PRODEDW", "DEVEDW", "TESTEDW")
EXPORT_DEFAULT_SCHEMA="DEV"

class ExportBaseForm(forms.Form):

  def __init__(self, data=None, prefix=None, initial=None, db=None):
    super(ExportBaseForm, self).__init__(data=data,
        prefix=prefix, initial=initial, auto_id=None)
    self._db = db

class ExportDBForm(ExportBaseForm):
  database = forms.CharField(required=True,
      initial=EXPORT_DBS[0])
  user = forms.CharField(required=True)
  password = forms.CharField(required=True, 
      widget=forms.PasswordInput())

  def clean(self):
    cleaned_data = self.cleaned_data
    if self._db and len(self._errors) == 0:
      try:
        self._db.connect(cleaned_data)
      except OperationalError as e:
        if "SQL30082N" in str(e):
          err_msg = _("Incorrect username or password.")
          err = self.error_class([err_msg])
          self._errors["password"] = err
        elif 'SQL1060N' in str(e):
          err_msg = 'User %s does not have the CONNECT privilege' % self.cleaned_data['user']
          err = self.error_class([err_msg])
          self._errors['user'] = err
        else:
          err = self.error_class([str(e)])
          self._errors["password"] = err
        del cleaned_data["user"]
        del cleaned_data["password"]
      except ProgrammingError as e:
        err_msg = "%s could not be found." % self.cleaned_data["database"] \
          if "SQL1013N" in str(e) else str(e)
        err = self.error_class([err_msg])
        self._errors["database"] = err
        del cleaned_data["database"]
      except Exception as e:
        err = self.error_class([str(e)])
        self._errors["user"] = err
        self._errors["password"] = err
        del cleaned_data["user"]
        del cleaned_data["password"]

    return cleaned_data

class ExportTableForm(ExportBaseForm):
  schema = forms.CharField(required=True,
      initial=EXPORT_DEFAULT_SCHEMA, max_length=128)
  table = forms.CharField(required=True, max_length=128)

  def clean_schema(self):
    schema = self.cleaned_data["schema"]
    if self._db and self._db.is_connected():
      if not self._db.has_schema(schema):
        raise forms.ValidationError("The schema %s doesn't exist." % schema)
    return schema

class ExportColumnForm(forms.Form):
  name = forms.CharField(required=True, max_length=40)
  hive_type = forms.CharField(required=True, max_length=20)
  db_type = forms.CharField(required=True, max_length=15)

  # def clean(self):
  #   super(ExportColumnForm,self).clean()

ExportColumnFormSet = formset_factory(ExportColumnForm, extra=0)

OP_CHOICES = (
    ('insert', 'Append'),
    ('replace', 'Replace') )
class ExportConfirmRecreationForm(ExportBaseForm):
  confirm_recreation = forms.BooleanField()

  def clean_confirm_recreation(self):
    confirm = self.cleaned_data.get("confirm_recreation")
    if confirm in (None, False):
      raise forms.ValidationError("You must confirm to recreate the table!")
    return confirm

class ExportConfirmOperationForm(ExportBaseForm):
  operation = forms.ChoiceField(widget=RadioSelect, choices=OP_CHOICES)
