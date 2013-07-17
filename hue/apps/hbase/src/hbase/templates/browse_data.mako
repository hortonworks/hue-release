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
