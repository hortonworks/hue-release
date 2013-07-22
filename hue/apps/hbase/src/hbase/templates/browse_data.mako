## Licensed to Hortonworks, inc. under one
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

${ commonheader(_('Hbase'), 'hbase', user) | n,unicode }
<%namespace name="actionbar" file="actionbar.mako" />

<div class="container-fluid" id="tables">
  <input type="hidden" id="table_name" value="${table.name}" />
  <%actionbar:render>
  <%def name="actions()">
  <a href="" class="btn toolbarBtn"> <i class="icon-plus-sign"></i>
    ${_('Add row')}</a>
  
  
  <button id="dropBtn" class="btn toolbarBtn" title="${_('Delete rows')}" data-bind="disable: slectedRows().length==0">
    <i class="icon-trash"></i>  ${_('Delete rows')}</button>

  <button id="dropBtn" class="btn toolbarBtn" title="${_('Browse all versions')}" 
          data-bind="click: getVersions,disable: slectedRows().length!=1">
    <i class=" icon-list-alt"></i>  ${_('Browse all versions')}</button>
  
</%def>
</%actionbar:render>
<div class="span11">
  <table class="table table-condensed table-striped
                datatables">
    <thead>
      <tr>
        <th><input type="checkbox" data-bind="click: selectAlldata" /></th>
        <th>Row key</th>
        <th>Family:Column</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody data-bind="foreach: rows">
      <tr>
        <td><input type="checkbox" data-bind="checked: selected" /></td>
        <td data-bind="text: row"></td>
        <td data-bind="text:column"></td>
        <td>
          <textarea data-bind="value: value"></textarea>
          <ul data-bind="foreach: versions">
            <li>
              <i class="icon-time"></i> <span data-bind="text: timestamp"></span><br>
              <span data-bind="text: prevValue"></span>
            </li>
          </ul>
        </td>
      </tr>
    </tbody>
  </table>
</div>
</div>
<script src="/static/ext/js/knockout-min.js" type="text/javascript"
        charset="utf-8"></script>

<script src="/hbase/static/js/browse_data.js" type="text/javascript"
        charset="utf-8"></script>


${ commonfooter(messages) | n,unicode }
