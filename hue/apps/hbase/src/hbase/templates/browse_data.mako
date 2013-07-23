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
  <a href="" class="btn toolbarBtn" data-bind="click: addRowModal"> <i class="icon-plus-sign"></i>
    ${_('Add row')}</a>
  
  
  <button id="dropBtn" class="btn toolbarBtn" title="${_('Delete rows')}" data-bind="disable: slectedRows().length==0">
    <i class="icon-trash"></i>  ${_('Delete rows')}</button>

  <button id="dropBtn" class="btn toolbarBtn" title="${_('Browse all versions')}" 
          data-bind="click: getVersions,disable: slectedRows().length!=1">
    <i class=" icon-list-alt"></i>  ${_('Browse all versions')}</button>

 </div>

</%def>
</%actionbar:render>
<div class="span12">

  <!--   <tbody data-bind="foreach: rows"> -->
  <!--     <tr> -->
  <!--       <td><input type="checkbox" data-bind="checked: selected" /></td> -->
  <!--       <td data-bind="text: row"></td> -->
  <!--       <td data-bind="text:column"></td> -->
  <!--       <td> -->
  <!--         <div><span data-bind="text: -->
  <!--         value"></span> <span class="badge -->
  <!--         badge-success"> -->
  <!--             <a data-bind="click: editValue" href="javascript:void(0);"><i class="icon-pencil"></i></a></span></div>  -->
  <!--         <ul data-bind="foreach: versions"> -->
  <!--           <li> -->
  <!--             <i class="icon-time"></i> <span data-bind="text: timestamp"></span><br> -->
  <!--             <span data-bind="text: prevValue"></span> -->
  <!--           </li> -->
  <!--         </ul> -->
  <!--       </td> -->
  <!--     </tr> -->
  <!--   </tbody> -->
  <!-- </table> -->
  



<!-- <div class="show-grid"> -->
<!--   <div class="span1" data-bind="text: row"></div> -->
<!--   <div class="row" data-bind="foreach: rows"> -->
<!--     <div class="span1" data-bind="text: row"></div> -->
<!--     <\!-- ko foreach: {data: columnFamilies, as: 'cf'} -\-> -->
<!--       <div data-bind="attr:{class: $parent.cfCount()}"> -->
<!--         <div data-bind="text: cf.cfName"></div> -->
<!--         <div data-bind="foreach: {data: cf.columns, as: 'col'}"> -->
<!--           <div data-bind="text: col.columnName"></div> -->
<!--           <div data-bind="text: col.value"></div> -->
<!--         </div> -->
<!--       </div>  -->
<!--       <\!-- /ko -\-> -->
<!--   </div> -->
<!-- </div> -->


<div class="row-fluid show-grid">
  <!-- ko foreach: rows -->
  <div class="span1" data-bind="text: row"></div>
  <div class="span10 offset1">
    <div class="accordion" data-bind="attr: {id: row}">
      <!-- ko foreach: {data: columnFamilies, as: 'cf'} -->
      <div class="accordion-group">
        <div class="accordion-heading">
          <a class="accordion-toggle collapsed" data-toggle="collapse"
             data-bind="text: cf.cfName,attr: {href: '#' + $parent.row() + cf.cfName(), 'data-parent': $parent.nameID()}">
          </a>
        </div>
        <div data-bind="attr: {id: $parent.row() + cf.cfName() }" class="accordion-body collapse"
             style="height: 0px;">
          <div class="pagination">
            <ul>
          <!-- ko foreach: {data: cf.columns, as: 'col'} -->
          <li>
            <a href="javascript:void(0);" data-bind="text:
            col.columnName() + ':'"></a>
          </li>
          <li>
            <a href="javascript:void(0);" data-bind="text: col.value()"></a>
          </li>
          <li><a href="javascript:void(0)">&nbsp;</a></li>
          <!-- /ko -->
            </ul>
          </div>
        </div>
      </div>
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->
</div>



</div>

<div class="modal hide fade" id="add_row"> 
 <form data-bind="submit: addRow">
     <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>Add row</h3>
  </div>
  <div class="modal-body">
    <p>
      <label class="control-label" for="rowKeyInput">
        Row Key:
      </label>
      <input type="text" id="rowKeyInput" required="required"
      data-bind="value: rowKeyValue"/>
      <label class="control-label" for="columnFamilySelect"> 
        Column Family: 
      </label> 
      <select id="columnFamilySelect" 
              data-bind="options: column_families,value: cfValue" 
              required="required" ></select> 
      <label class="control-label" for="columnInput"> 
        Column: 
      </label>
      <input type="text" id="columnInput" required="required"
      data-bind="value: columnValue" />
      <label class="control-label" for="valueInput"> 
        Value: 
      </label>
      <input id="valueInput" type="text" required="required"
      data-bind="value: valueVal" />
      
    </p>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
    <button type="submit">Add row</button>
  </div>
  </form>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript"
        charset="utf-8"></script>
<script src="/hbase/static/js/knockout.validation.js" type="text/javascript" charset="utf-8"></script>
<script src="/hbase/static/js/browse_data.js" type="text/javascript"
        charset="utf-8"></script>

<link rel="stylesheet" href="/hbase/static/css/hbase.css" type="text/css" media="screen" />

${ commonfooter(messages) | n,unicode }
