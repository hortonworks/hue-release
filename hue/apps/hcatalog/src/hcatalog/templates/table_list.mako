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

<table class="table table-condensed table-striped datatables">
    <thead>
    <tr>
        <th width="1%"><div class="hueCheckbox selectAll" data-selectables="tableCheck"></div></th>
        <th>${_('Table Name')}</th>
        <th>&nbsp;</th>
    </tr>
    </thead>
    <tbody>
            % for table in tables:
            <tr>
                <td data-row-selector-exclude="true" width="1%">
                    <div class="hueCheckbox tableCheck"
                         data-drop-name="${ table }" data-row-selector-exclude="true"></div>
                </td>
                <td>
                    <a href="${ url(app_name + ':describe_table', database=database, table=table) }" data-row-selector="true">${ table }</a>
                </td>
                <td>
                    <a href="${ url(app_name + ':read_table', database=database, table=table) }" data-row-selector="true" class="btn btn-primary browse" onclick="onBrowse()">${_('Browse Data')}</a>
                </td>
            </tr>
            % endfor
    </tbody>
</table>