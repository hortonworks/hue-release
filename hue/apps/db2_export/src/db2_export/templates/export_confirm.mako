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
from db2_export.models import ExportState
from django.utils.translation import ugettext as _
%>
<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="export" file="export_components.mako" />

${commonheader(_("Export to Database"), app_name, user, "100px") | n,unicode }
${layout.menubar(section='tables')}
${export.open_container(query_id)}
  ${export.step_list(wizard)}
  ${export.open_form(query_id)}
  <div class="stepDetails">
    <fieldset>
      % if recreation:
        <div class="alert alert-info"><h3>${_("Confirm Recreate the Target Table!")| n,unicode}</h3></div>
        <div class="alert">
          <strong>${_('Warning!')}</strong>${export.table_name(table)} exists.
        </div>
        <div class="control-group">
          <label class="control-label" for="recreation">Confirm recreation</label>
          <div class="controls">
            <input id="recreation" type="checkbox" name="confirm_recreation" />
            <span class="help-block">${_('Exporter currently only supports to <strong>DROP</strong> the table, and <strong>CREATE</strong> it using the schema defined in the previous page. Please check the box if you are ok with this.')| n,unicode}</span>
          </div>
        </div>
        ${export.wizard_buttons(query_id, wizard)}
      % else:
        <div class="alert alert-info"><h3>${_("Choose Append or Replace Data")}</h3></div>
        <div class="alert">
          ${export.table_name(table)} exists, and its schema is <strong>compatible</strong> with your definition. You can choose to append the query result to that table or overwrite the whole table.
        </div>
        <div class="clearfix">
          ${export.render_field(confirm["operation"])}
        </div>
        ${export.wizard_buttons(query_id, wizard)}
      % endif
    </fieldset>
  ${export.close_form()}
  </div>
${export.close_container()}

<script type="text/javascript">
  $(document).ready(function(){
    $("#step4").click(function(e){
      e.preventDerault();
      $("input[name='export-submit']").click();
    });
    $("body").keypress(function(e){
      if(e.which == 13){
        e.preventDerault();
        $("input[name='export-submit']").click()
      }
    });
  });
</script>

${commonfooter(messages) | n,unicode }
