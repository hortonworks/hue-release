<%!
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

${ commonheader(_('Hbase'), 'hbase', user) | n,unicode }
<%namespace name="actionbar" file="actionbar.mako" />

<div class="container-fluid" id="tables">
          <%actionbar:render>
            <%def name="actions()">
                <a href="/hbase/table/new" class="btn toolbarBtn"> <i class="icon-plus-sign"></i>
                ${_('Create new table')}</a>

                <button id="browseBtn" class="btn toolbarBtn"
                title="${_('Compact the selected table')}"
                data-bind="enable: selectedFilter().length, click: askCompactionType"><i class="icon-hdd"></i>
                ${_('Compact')}</button>

                <button id="browseBtn" class="btn toolbarBtn"
                title="${_('Enable tables')}"
                data-bind="enable: disabledFilter().length, click: enableTables"><i class="icon-eye-open"></i>
                ${_('Enable tables')}</button>

                <button id="dropBtn" class="btn toolbarBtn"
                title="${_('Disable selected tables')}"
                data-bind="enable: enabledFilter().length, click: disableTables" >
                  <i class="icon-eye-close"></i>  ${_('Disable')}</button>            
                
                <button id="dropBtn" class="btn toolbarBtn"
                        title="${_('Delete the selected tables')}"
                        data-bind="click: confirmDelete, enable: selectedFilter().length">
                  <i class="icon-trash"></i>  ${_('Drop')}</button>

          </%def>
          </%actionbar:render>
<div class="span11" ><div data-bind="text: enabledFilter().lenght"></div> 
  
  <div class="progress" style="display: none;" id="op_progres">
    <div class="bar" style="width: 0%;"></div>
  </div>
            <table class="table table-condensed table-striped
                          datatables">
                <thead>
                  <tr>
                    <th width="1%"><input type="checkbox" name="" value="" class="" /></th>
                    <th width="80%">${_('Table Name')}</th>
                    <th>&nbsp;</th>
                  </tr>
                </thead>
                <tbody data-bind="foreach: tables">
                  <tr>
                    <td data-row-selector-exclude="true" width="1%">
                      <input type="checkbox" data-bind="checked: selected"/>
                    </td>
                    <td>
                      <a data-bind="attr: {href: url}, html: disabledName()"></a>
                    </td>
                    <td><a data-bind="attr: {href: browseDataUrl}" class="btn btn-primary browse" >Browse Data</a></td>

                  </tr>
                </tbody>
            </table>
        </div>
</div>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/hbase/static/js/tables.js" type="text/javascript"></script>



<div class="modal hide fade alert alert-block alert-error fade in"
     id="tableAlert" role="dialog">
  <button type="button" class="close" data-dismiss="alert">×</button>
  <h4 class="alert-heading" id="alertText"></h4>
  <p>
    <a class="btn" href="#" data-dismiss="modal">OK</a>
  </p>
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


<div id="modal-from-dom" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
         <h3>Delete Tables?</h3>
    </div>
    <div class="modal-body">
        <p>You are about to delete next tables:</p>
        <p>
          <ul id="deleteTableList">
            
          </ul>
        </p>
        <p>Are you sure you want to delete them?</p>
    </div>
    <div class="modal-footer">
        <a class="btn danger" data-bind="click: deleteTables">Yes</a>
        <a href="javascript:$('#modal-from-dom').modal('hide')" class="btn secondary">No</a>
    </div>
</div>

${ commonfooter(messages) | n,unicode }
