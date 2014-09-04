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
${export.open_container(query_id)}
  ${export.step_list(wizard) }
  ${export.open_form(query_id) }
    <div class="stepDetails">
      <fieldset>
        <div class="alert alert-info">
          <h3>${_('Define Database Table Columns')}</h3>
          ${_('Please confirm names and data types for each columns.')}
        </div>
        <div>
          <table class="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Column</th>
                <th>Hive Data Type</th>
                <th>DB2 Data Type</th>
              </tr>
            </thead>
            <tbody>
              ${export.column_table(columns)}
            </tbody>
          </table>
        </div>
      </fieldset>
    </div>
    ${ unicode(columns.management_form) | n }
    ${ export.wizard_buttons(query_id, wizard) }
  ${ export.close_form() }
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
