<%!
from django.utils.translation import ugettext as _
%>

<%def name="my_scripts(pig_scripts)">
  <h4 class="pull-left"> ${_('My scripts')} </h4>
<div class="nav-header script_list_header">
  <a  class="pull-right new_script" data-placement="right" rel="tooltip" title="New script"
      href="${url('root_pig')}?new=true"> <i class="icon-plus-sign"></i> ${_('New script')}</a>
</div>

<div class="script_list">
% if pig_scripts:
  <ul class="nav nav-list">
    % for v in pig_scripts:
    <li id="copy" >
      <p>
        <a href="${url('pig.views.delete', v.id)}" onclick="return confirm('Are you sure, you want to delete this script?');">
          <img src="/pig/static/art/delete.gif" alt="Delete" title="Delete script" height="12" width="12">
        </a>
        <a href="${url("clone", v.id)}" class="clone" value="${v.id}">
          <img src="/pig/static/art/clone.png" alt="Clone" title="Clone script" height="14" width="14">
        </a>
        <a href="${url('pig.views.index', obj_id=v.id)}">
          % if v.title:
          ${v.title}
          % else:
          no title
          % endif
        </a>
      </p>
    </li>
    % endfor
  </ul>
% else:
  <small><i>${_('No scripts yet')}</i></small>
% endif
</div>

<style>

.script_list_header {
  height:40px;
  position: relative;
}

.script_list {
  overflow-y: auto;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
  box-shadow: inset 0 1px 1px rgba(0,0,0,0.05);
  padding: 6px;
  max-height: 290px;
}
.script_list p {
  margin: 0 0 0px;
}

.new_script {
  position: absolute;
  bottom: 0px;
  right: 0;
}

</style>

</%def>


<%def name="udfs(udfs)">
  % for udf in udfs:
      <a href="${url('udf_delete', udf.id)}"  onclick="return confirm('Are you sure, you want to delete this udf?');">
          <img src="/pig/static/art/delete.gif" alt="Delete" height="12" width="12" title="Delete UDF"> </a>
      <a class="udf_register" href="#" value="${udf.file_name}">${udf.file_name}</a><br />
  % endfor
  </%def>


<%def name="modal(items)">
  <%
    opt = {
      'windowId': 'modalConfirm',
      'cBtnId': '',
      'cBtnText': '',
      'cBtnClass': 'btn primary',
      'cBtnAttr': '',
      'title': '',
      'textbody': '',
      'htmlbody': '',
      'cancelBtn': True,}

    opt.update(items)
  %>
  <div id="${opt['windowId']}" class="modal hide fade" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
      <h3>${_(opt['title'])}</h3>
    </div>
    <div class="modal-body">
    % if opt['htmlbody']:
      ${opt['htmlbody']|n, unicode}
    % else:
      <p>${opt['textbody']}</p>
    % endif
    </div>
    <div class="modal-footer">
      % if opt['cancelBtn']:
      <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
      % endif
      <button id="${opt['cBtnId']}" class="${opt['cBtnClass']}" ${opt['cBtnAttr']|n,unicode}>${_(opt['cBtnText'])}</button>
    </div>
  </div>
</%def>
