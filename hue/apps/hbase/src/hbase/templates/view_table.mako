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
  <input type="hidden" id="table_ebabled" value="${int(is_enabled)}" />
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    
                    <li>
                      <a href="javascript:void(0);"
                      data-bind="visible: isEnabled, click: disableTable">${_('Disable table')}</a>
                    </li>
                    
                    <li>
                      <a href="javascript:void(0);"
                         data-bind="visible: !isEnabled, click: enableTable">${_('Enable table')}</a>
                    </li>

                    <li>
                       <a href="javascript:void(0);"
                          data-bind="click: compactTableModal">${_('Compact  table')}</a>
                    </li>

                    <li>
                      <a href="javascript:void(0);" data-bind="click: dropTableConfirm">${_('Drop table')}
                      </a>
                    </li>

                    <li>
                      <a href="/hbase/table/browse/${table.name}">${_('Browsea data')}</a>
                    </li>
                    
                    <li>
                      <a href="/hbase/table/browse/pig/${table.name}">${_('View in pig')}</a>
                    </li>
                    
                </ul>
            </div>
        </div>
        <div class="span9">
          <div class="span4">
          <table class="table-hover table-condensed table-bordered">
            <caption>Column Families</caption>
            <thead>
              <tr>
                <th>Name</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              % for cf, options in table.families().iteritems():
              <tr>
                <td>${cf}</td>
                <td>
                  <ul>
                    % for k,v in options.iteritems(): 
                    <li>${k}: ${v}</li>
                    % endfor
                  </ul>
                </td>
              </tr>
              % endfor
            </tbody>
          </table>
          </div>
          <div class="span4">
            <table class="table-hover table-condensed table-bordered">
              <caption>Regions</caption>
              <tbody>
                % for region in table.regions():
                <tr>
                  <td>
                    <ul>
                      % for k,v in region.iteritems():
                      <li>${k}: ${v}</li>
                      % endfor
                    </ul>
                  </td>
                </tr>
                % endfor
            </table>
          </div>
        </div>
    </div>
</div>


<div id="modal-from-dom" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
         <h3>Delete Table?</h3>
    </div>
    <div class="modal-body">
        <p>You are about to delete this table?</p>
    </div>
    <div class="modal-footer">
        <a class="btn danger" data-bind="click: dropTable">Yes</a>
        <a href="javascript:$('#modal-from-dom').modal('hide')" class="btn secondary">No</a>
    </div>
</div>


<div id="compactionModal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3>Choose compaction type</h3>
  </div>
  <div class="modal-body">
    <p>
      <input type="radio" name="compactionType" value="major" />Major
      <input type="radio" name="compactionType" value="minor" checked/>Minor
    </p>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
    <button class="btn btn-primary" data-bind="click: compact">Compact</button>
  </div>
</div>


<script type="text/javascript"
        src="/hbase/static/js/view_table.js"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript"
        charset="utf-8"></script>
${ commonfooter(messages) | n,unicode }
