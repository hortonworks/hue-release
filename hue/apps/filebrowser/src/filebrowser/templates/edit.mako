## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%namespace name="edit" file="editor_components.mako" />
<%!
  from django.template.defaultfilters import urlencode
  from filebrowser.views import truncate
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>
<%
  path_enc = urlencode(path)
  dirname_enc = urlencode(dirname)
%>
<%namespace name="fb_components" file="fb_components.mako" />

${ commonheader(_('%(filename)s - File Viewer') % dict(filename=truncate(filename)), 'filebrowser', user) | n,unicode }

<div class="container-fluid">
	% if breadcrumbs:
        ${fb_components.breadcrumbs(path, breadcrumbs)}
	%endif
</div>

<div class="container-fluid">
<div class="well" >
    <form id="saveForm" class="form-stacked" method="post" action="${url('filebrowser.views.save_file')}"> ${ csrf_token_field | n } 
    <div class="toolbar">
		<a class="btn" href="${url('filebrowser.views.view', path=dirname_enc)}">${_('View Location')}</a>
	</div>
	<br/>

% if form.errors:
  <div class="alert-message">
    % for field in form:
      % if len(field.errors):
       ${unicode(field.errors) | n}
      % endif
    % endfor
  </div>
% endif
        ${edit.render_field(form["path"], hidden=True, notitle=True)}
        ${edit.render_field(form["encoding"], hidden=True, notitle=True)}

        <div style="width: 100%; height: 100%;">${edit.render_field(form["contents"], tag="textarea", notitle=True, attrs=dict(
          style="width:100%; height:400px;")) | n}</div>
        <input class="btn btn-primary" type="submit" name="save" value="${_('Save')}">
        <a id="saveAsBtn" class="btn">${_('Save As')}</a>
    </form>
</div>


<div id="saveAsModal" class="modal hide fade">
    <form id="saveAsForm" action="${url('filebrowser.views.save_file')}" method="POST" class="form-stacked form-padding-fix"> ${ csrf_token_field | n } 
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Save As')}</h3>
    </div>
    <div class="modal-body">
      <div class="control-group path">
        ${edit.render_field(form["path"], notitle=True, klass="xlarge", attrs={'id':'path-input'})}
        <span class="help-block">${_("Enter the location where you'd like to save the file.")}</span>
      </div>
    </div>
    <div class="modal-footer">
        <div id="saveAsNameRequiredAlert" class="alert-message fieldError hide" style="position: absolute; left: 10;">
            <p><strong>${_('Name is required.')}</strong>
        </div>
		${edit.render_field(form["contents"], hidden=True)}
		${edit.render_field(form["encoding"], hidden=True)}
        <a id="cancelSaveAsBtn" class="btn">${_('Cancel')}</a>
        <input type="submit" value="${_('Save')}" class="btn btn-primary" />
    </div>
    </form>
</div>

  <script type="text/javascript" charset="utf-8">
    $(document).ready(function () {
      $("#saveAsBtn").click(function () {
        $("#saveAsModal").modal({
          backdrop: "static",
          keyboard: true,
          show: true
        })
      });

      $("#cancelSaveAsBtn").click(function () {
        $("#saveAsModal").modal("hide");
      });

      function submitForm(form) {
        var form_data = {};
        $.map($(form).serializeArray(), function(n, i){
            form_data[n['name']] = n['value'].replace(/\r\n/g,'\n');
        });
        $.ajax({
          url:"${url('filebrowser.views.save_file')}",
          type:'post',
          dataType:'json',
          data:form_data,
          success:function(data){
            window.location.replace(data.path)
          },
          error:function(data){
            $.jHueNotify.error("${_('There was a problem with your request.')}");
            resetPrimaryButtonsStatus();
          }
        });
      }

      $('#saveForm').submit(function (e){
        e.preventDefault();
        submitForm(this);
      });

      $("#saveAsForm").submit(function (e){
        e.preventDefault();
        if ($.trim($("#path-input").val()) == "") {
          $("#saveAsForm").find(".path").addClass("error");
          $("#saveAsNameRequiredAlert").show();
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }
        submitForm(this);
      });

      $("#path-input").focus(function () {
        $("#saveAsForm").find(".path").removeClass("error");
        $("#saveAsNameRequiredAlert").hide();
      });
    });
  </script>

${ commonfooter(messages) | n,unicode }


