## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>
<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="export" file="export_components.mako" />

${commonheader(_("Export to Database"), app_name, user, "100px") | n,unicode }
${layout.menubar(section='tables')}
<%
  required = { 'class': 'required' }
%>
${export.open_container(query_id)}
  ${export.step_list(wizard)}
  ${export.open_form(query_id)}
    <div class="stepDetails">
      <fieldset>
        <div class="alert alert-info">
          <h3>${_('Specify Database and Table!')}</h3>
          ${_("Please select the database and table to where you want export the query result. You need to provide the credentials to log on the database.")}
        </div>
        <div class="control-group">
          ${comps.bootstrapLabel(db["database"])}
          <div class="controls">
            ${comps.field(db["database"], show_errors=False)}
            <span  class="help-inline">${unicode(db["database"].errors) | n}</span>
          </div>
        </div>
        <div class="control-group">
          ${comps.bootstrapLabel(table["schema"])}
          <div class="controls">
            ${comps.field(table["schema"], show_errors=False)}
            <span  class="help-inline">${unicode(table["schema"].errors) | n}</span>
          </div>
        </div>
        <div class="control-group">
          ${comps.bootstrapLabel(table["table"])}
          <div class="controls">
            ${comps.field(table["table"], placeholder="DB2 table name", show_errors=False)}
            <span  class="help-inline">${unicode(table["table"].errors) | n}</span>
          </div>
        </div>
        <div class="control-group">
          ${comps.bootstrapLabel(db["user"])}
          <div class="controls">
            ${comps.field(db["user"], placeholder="DB2 user name", show_errors=False)}
            <span  class="help-inline">${unicode(db["user"].errors) | n}</span>
          </div>
        </div>
        <div class="control-group">
          ${comps.bootstrapLabel(db["password"])}
          <div class="controls">
            ${comps.field(db["password"], placeholder="DB2 password", show_errors=False, attrs={"type": "password"})}
            <span  class="help-inline">${unicode(db["password"].errors) | n}</span>
          </div>
        </div>
      </fieldset>
    </div>
    ${export.wizard_buttons(query_id, wizard)}
  ${export.close_form()}
${export.close_container()}

<script type="text/javascript" charset="utf-8">
  $(document).ready(function(){
    $("#step2").click(function(e){
      e.preventDefault();
      $("input[name='export-submit']").click();
    });
    $("body").keypress(function(e){
      if(e.which == 13){
        e.preventDefault();
        $("input[name='export-submit']").click();
      }
    });
  });
</script>

${commonfooter(messages) | n,unicode }

