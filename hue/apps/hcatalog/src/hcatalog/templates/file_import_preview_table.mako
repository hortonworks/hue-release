## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
## http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.

<%!
    from desktop.views import commonheader, commonfooter
    from django.utils.translation import ugettext as _
%>

<%namespace name="comps" file="beeswax_components.mako" />

<table class="table table-striped table-condensed resultTable" cellpadding="0" cellspacing="0" data-tablescroller-min-height-disable="true" data-tablescroller-enforce-height="true">
    <thead>
    <tr>
        <th>&nbsp;</th>
        % for form in column_formset.forms:
                <th>
                ${comps.label(form["column_name"])}
                ${comps.field(form["column_name"],
                render_default=False,
                klass="column",
                placeholder=_("Column name")
                )}
                    <span  class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                    <span  class="help-inline error-inline error-inline-bis hide">${_('Column names must be unique.')}</span>
                 <br/><br/>
                ${comps.label(form["column_type"])}
                ${comps.field(form["column_type"],
                render_default=True
                )}
                ${unicode(form["_exists"]) | n}
                </th>
        %endfor
    </tr>
    </thead>
    <tbody>
    <% max_row_len = max([len(row) for row in fields_list])%>
    % for i, row in enumerate(fields_list):
        <tr>
            <td><em>${_('Row')} #${row_start_index + i + 1}</em></td>
        <% cur_row_len = len(row)%>
        % for val in row:
                <td>${val}</td>
        % endfor
        ## aligning the table with empty cells
        % for i in range(max_row_len - cur_row_len):
                <td></td>
        % endfor
        </tr>
    % endfor
    </tbody>
</table>