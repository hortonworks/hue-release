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
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    % if is_enabled:
                    <li><a href="/hbase/table/drop/${table.name}">${_('Disable table')}</a></li>
                    % else:        
                    <li><a href="/hbase/table/drop/${table.name}">${_('Enable table')}</a></li>
                    % endif
                    <li><a href="/hbase/table/drop/${table.name}">${_('Drop table')}</a></li>
                    <li><a href="/hbase/table/browse/${table.name}">${_('Brows data')}</a></li>
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


${ commonfooter(messages) | n,unicode }
