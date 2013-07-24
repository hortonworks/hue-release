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

<div class="container-fluid" id="tables">
  <input type="hidden" id="table_name" value="${table.name}" />
  

  <div class="well" style="padding-top: 10px; padding-bottom: 0">
    <div class="pull-right" style="margin:0"></div>
    <div style="margin: 0px 0px 10px 0px">
      <form data-bind="submit: filterData"><input name="filter" type="text" data-bind="value: queryFilter"
             class="input-xlarge search-query"
             placeholder="row_key1,row_key2 ...">&nbsp;&nbsp;&nbsp;&nbsp;

      <a href="" class="btn toolbarBtn" data-bind="click: addRowModal"> <i class="icon-plus-sign"></i>
        ${_('Add row')}
      </a>
      </form>
    </div>
  </div>
 
</div>


<div class="span11">


 
  <!-- ko foreach: {data: rows, as: 'r'} -->
  <div class="row-fluid show-grid">
    <div class="span1">
      <div data-bind="text: r.row"></div>
      <a data-bind="click: dropRow" href="javascript:void(0);"><i class="icon-trash" title="Drop row"></i></a>
    </div>
    <div class="span10 offset1">
      <div class="accordion" data-bind="attr: {id: r.row}">
        <!-- ko foreach: {data: columnFamilies, as: 'cf'} -->
        <div class="accordion-group">
          <div class="accordion-heading">
            <a class="accordion-toggle collapsed" data-toggle="collapse"
               data-bind="text: cf.cfName,attr: {href: '#' +
               $parent.row() + cf.cfName(), 'data-parent': '#' + $parent.row()}">
            </a>
          </div>
          <div data-bind="attr: {id: $parent.row() + cf.cfName() }" class="accordion-body collapse"
               style="height: 0px;">
            
                <!-- ko foreach: {data: cf.columns, as: 'col'} -->
                <div class="span2">
                  <div class="modal-header">
                    <h3 data-bind="text: col.columnName"></h3>
                  </div>
                  <div class="modal-body">
                    <p data-bind="text: col.value, attr: {id: 'p_' + col.rowID()}" ></p>
                    <textarea data-bind="value: col.editValue,
                                         attr:{id: col.rowID()}"
                    style="display:none;" ></textarea>
                    <div data-bind="foreach: {data: col.versions, as: 'version'}">
                        <p><i class=" icon-time"></i><span data-bind="text: version.timestamp"></span></p>
                        <p data-bind="text: version.prevValue"></p>
                    </div>
                      
                    <a href="javascript:void(0);" data-bind="click: editCell">
                      <i class="icon-pencil" title="Edit cell"></i>
                      <i class="icon-ok" title="Save cell" style="display:none;"></i>
                    </a>
                    <a href="javascript:void(0)"
                       data-bind="click: getVersions">
                      
                      <i class="icon-eye-open" title="Browse previous versions"></i>
                    </a>
                    <a href="javascript:void(0)" data-bind="click:  dropCell"><i class="icon-trash" title="Remove cell"></i></a>
                  </div>
                </div>
                <!-- /ko -->
          </div>
        </div>
        <!-- /ko -->
      </div>
    </div>
  </div>
  <!-- /ko -->


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
    <button class="btn btn-success" type="submit">Add row</button>
  </div>
  </form>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript"
        charset="utf-8"></script>
<script src="/hbase/static/js/knockout.validation.js"
        type="text/javascript" charset="utf-8"></script>
<script src="/hbase/static/js/json2.js" type="text/javascript" charset="utf-8"></script>
<script src="/hbase/static/js/browse_data.js" type="text/javascript"
        charset="utf-8"></script>

<link rel="stylesheet" href="/hbase/static/css/hbase.css" type="text/css" media="screen" />

${ commonfooter(messages) | n,unicode }
