## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.


<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared"  file="shared_components.mako" />
<%namespace name="my_scripts" file="my_scripts.mako" />
${commonheader("Pig", "pig", user, "100px")| n,unicode}
<%shared:menubar section='My Scripts' />

<%!
from django.utils.translation import ugettext as _
from pig import conf
UDF_PATH = conf.UDF_PATH.get()
%>

## Use double hashes for a mako template comment
## Main body


${my_scripts.modal({
  'windowId':'show-modal-for-var',
  'cBtnId':'save-values-for-var',
  'cBtnText':'Save',
  'title':'Please specify parameters for this variable(s):',
  'htmlbody':'<div class="clearfix">\
                <div class="modal-for-var-input-warp">\
                </div>\
              </div>',
  'cancelBtn': False,
})}

${my_scripts.modal({
  'windowId':'udfRmConfirm',
  'title': 'Confirm Delete',
  'textbody': 'Are you sure, you want to delete this udf?',
  'cBtnId': 'rmUdfBtn',
  'cBtnText':'Delete',
  'cBtnAttr': 'data-bind="click: rm_confirm"',
  'cBtnClass':'btn btn-danger',
})}

${my_scripts.modal({
  'windowId':'onRunJobSave',
  'cBtnId': 'runningJobSaveBtn',
  'cBtnText':'Save and switch',
  'title': 'Job is running.',
  'textbody': 'Are you sure, you want to switch to edit mode?',
})}

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3" style="float: left;">
      <div class="well sidebar-nav">
        ${my_scripts.my_scripts(result['scripts'])}
        <h5 >${_('Settings')}</h5>
          <ul class="nav nav-list">
            <li>
              <label class="checkbox ">
                <input class="email" type="checkbox"
                   % if result.get("email_notification"):
                   checked="checked"
                   % endif
                   />${_('Email notification')}</label>
            </li>
            <li  class="nav-header">
              <div class="accordion" id="accordion3" >
                <div class="accordion-group">
                  <div class="accordion-heading">
                    <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion3" href="#collapseOne2">
                      ${_('User-defined Functions')}<i class="icon-chevron-down"></i>
                    </a>
                  </div>
                  <div id="collapseOne2" class="accordion-body collapse" style="text-transform:none;">
                    <div class="accordion-inner">
                      <!-- ko foreach: {data: udflist, as: 'udf'} -->
                        <a data-bind='click: $root.rmUdf' href="#">
                            <img src="/pig/static/art/delete.gif" alt="Delete" height="12" width="12" title="Delete UDF">
                        </a>
                        <a class="udf_register" href="#" data-bind="click: $root.putToEditor, text: udf.file_name"></a>
                        <br/>
                      <!-- /ko -->
                      <input type="hidden" class="get_udf_url" value="${url('udf_get')}">
                      <input type="hidden" class="del_udf_url" value="${url('udf_delete')}">
                    </div>
                  </div>
                </div>
              </div>
            </li>
            <li>
              <form id="udfs_form" enctype="multipart/form-data"
                  action="${url('pig.views.udf_create')}"
                  method="post" data-destination="${UDF_PATH}"> ${ csrf_token_field | n }
                  <div id="udf_file_upload"><i class="icon-upload icon-white"></i>${_('Upload UDF jar')}</div>
              </form>
            </li>
          </ul>
      </div>
    </div>
    <div class="span9" style="float: left; width: 70%;">
      <div class="clearfix">
        <div class="input">
          <form  action="${url("root_pig")}" method="post" id="pig_script_form"> ${ csrf_token_field | n }
            <input type="hidden" name="script_id"  value="${result.get('id','')}" >
            <div class="control-group">
              <div class="input-prepend">
                <div class="controls">
                <label class="control-label add-on" for="id_title">${_('Title:')}</label>
                  <input class="span2" id="id_title" type="text" name="title"
                          required="required" maxlength="200" value="${result.get('title',"")}">
                </div>
              </div>
            </div>

            <label class="script_label" for="id_pig_script" >
              <span>Pig script:</span>
              <span>
                <a href="javascript:void(0);" ><i class="icon-question-sign" id="help"></i></a>
                <div id="help-content" class="hide">
                  <ul>
                    <li class="text-success">${_('Press ctrl+space for autocompletion')}</li>
                    <li class="text-success">${_('To see table fields helper type table_name + "." (e.g. sample_07.)')}</li>
                  </ul>
                </div>
              </span>
            </label>
            <div class="pig_helper_wrap">
              <%include file="pig_helper.html" />
            </div>
            <textarea id="id_pig_script" required="required" rows="10" cols="40" name="pig_script" class="hide">${result.get("pig_script", "")}</textarea>
            % if result.get("python_script"):
            <div id="python_textarea">
              <label class="script_label" for="python_code">${_('Python UDF:')}</label>
              <textarea id="python_code" name="python_script" rows="4" >${result['python_script']}</textarea>
            </div>
            % else:
            <div id="python_textarea"style="display:none;" >
              <label class="script_label" for="python_code">${_('Python UDF:')}</label>
              <textarea id="python_code" name="python_script"></textarea>
            </div>
            % endif
            <div class="progress progress-striped active">
            <div class="bar" style="width: 0%;"></div>
          </div>
	          <input type="hidden" name="email" class='intoemail' />
            <input type="hidden" id="operation_type" />
            <div id="pigArguments">
              <div class="input-prepend input-append">
                <input type="text" name placeholder="e.g. -useHCatalog" class="pigArgument span2"/><span class="add-on"><i class="icon-arrow-left"></i> pig arguments</span>
              </div>
            </div>
	          <br>
            <div class="actions">
	            <input class="btn primary" type="submit" name="submit_action" id="save_button"
                   value="Save"
                   % if result.get("id"):
                   disabled="disabled"
                   % endif
                   />
              <%
                runningJob = result.get("job_id") and result.get("JOB_SUBMITTED")
                hideaction = 'display:none;'
              %>
	            <input class="btn primary action_btn" type="button" id="start_job" name="submit_action" value="Execute" style="${ hideaction if runningJob else ''}"/>
              <input class="btn primary " type="button"id="kill_job"  value="Kill job" style="${ hideaction if not runningJob else ''}" />
              <img id="spinner" src="/static/art/spinner.gif" class="hide" />
	            <input class="btn primary action_btn" type="button"id="explain" name="submit_action" value="Explain" style="${ hideaction if runningJob else ''}"/>
	            <input class="btn primary action_btn" name="submit_action"type="button" value="Syntax check" id="syntax_check" style="${ hideaction if runningJob else ''}"/>
	          </div>
	        </form>
          <input type="hidden" id="fakeArgs">
        </div>
        <div class="div_conteiner">
          ## result section
          <a class="btn-success btn-mini"
            % if 'stdout' in result and 'job_id' in result:
            href="${url("download_job_result", job_id=result['job_id'])}"
            % else:
            style="display:none;"
            % endif
            id="download_job_result">
          <i class="icon-download-alt"></i></a>
          <div class="alert alert-success ${'hide' if 'stdout' not in result else ''}" id="job_info_outer">
            <pre id="job_info">${result['stdout'] if 'stdout' in result else ''|h}</pre>
          </div>
          
          ## alert section
          <div class="alert alert-error hide" id="failure_info"></div>

          ## log section
          <div class="accordion alert alert-warning ${'hide' if 'stdout' not in result else ''}" id="accordion2">
            <div class="accordion-group">
              <div class="accordion-heading">
                <a class="accordion-toggle" data-toggle="collapse" id="job_logs" data-parent="#accordion2" href="#collapseOne">
                  ${'Logs...' if 'stdout' in result else ''}
                </a>
              </div>
              <div id="collapseOne" class="accordion-body collapse">
                  <pre class="accordion-inner" id="log_info">${result['error'] if 'stdout' in result else ''}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<link href="/pig/static/css/codemirror.css" rel="stylesheet">
<link href="/pig/static/css/simple-hint.css" rel="stylesheet">
<link href="/pig/static/css/show-hint.css" rel="stylesheet">
<link href="/pig/static/css/bootstrap-fileupload.min.css" rel="stylesheet">
<link href="/pig/static/css/bootstrap-tagmanager.css" rel="stylesheet">

<style type="text/css" media="screen">
.CodeMirror{
  height: 300px;
}
.CodeMirror-focused span.cm-CodeMirror-matchhighlight {
  background:  #e7e4ff; !important; 
}
label.valid {
  width: 24px;
  height: 24px;
  color: green;
  display: inline-block;
  text-indent: -9999px;
}
label.error {
  font-weight: bold;
  color: red;
  padding: 2px 8px;
  margin-top: 2px;
}
.pagination_controls a, .pagination_controls span {
  display: block;
  float: left;
  padding: 3px ;
}
.progress {
  -webkit-border-radius: 0;
  -moz-border-radius: 0;
  border-radius: 0;
}
.script_label {
  display: inline-block;
  background-color: #eee;
  padding: 5px;
  margin-bottom: 0;
  vertical-align: bottom;
  cursor: pointer;
  width: 85px;
}
.script_label:hover {
  box-shadow: inset 0px 0px 1px 1px #bbb;
}
.CodeMirror {
  border: 2px solid #eee;
}
#pigArguments .help-inline {
  margin-right: 5px;
}
#pigArguments > div {

  white-space: normal;
}
.pigArg{
  vertical-align: top;
}
.popover i {
  float: right;
  cursor: pointer;
  opacity: 0.4;
}
.pig_helper_wrap{
  display: inline-block;
  margin-bottom: 3px;
}
#spinner {
  margin-left: 15px;
}
</style>

<script type="text/javascript" src="/pig/static/js/jquery.validate.min.js"></script>
<script src="/pig/static/js/codemirror.js"></script>
<script src="/pig/static/js/pig.js"></script>
<script src="/pig/static/js/python.js"></script>
<script src="/pig/static/js/simple-hint.js"></script>
<script src="/pig/static/js/show-hint.js"></script>
<script src="/pig/static/js/pig-hint.js"></script>
<script src="/pig/static/js/hcat-helper.js"></script>
<script src="/pig/static/js/jquery.pagination.js"></script>
<script src="/pig/static/js/searchcursor.js"></script>
<script src="/pig/static/js/match-highlighter.js"></script>
<script src="/pig/static/js/emacs.js"></script>
<script src="/pig/static/js/pig_scripts.js"></script>
<script src="/pig/static/js/bootstrap-fileupload.min.js"></script>
<script src="/pig/static/js/bootstrap-tagmanager.js"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript"></script>
<script type="text/javascript">
var percent = 0;
var globalTimer = null;
var job_id = null;

function get_job_result(job_id)
{
    $.post("${url("get_job_result")}", {job_id: job_id}, function(data){
        if (data.error==="" && data.stdout==="" && percent <= 100)
        {
            globalTimer = window.setTimeout("get_job_result('"+job_id+"');", 3000);
            percent += 5;
            $(".bar").css("width", percent+"%");
            return;
        }

        if (parseInt(data.exit)==0) $(".bar").addClass("bar-success");
        else $(".bar").addClass("bar-danger");

        $("#download_job_result").show();
        $("#download_job_result").attr("href", "/pig/download_job_result/" + job_id + "/");
        //var stdout = escape(data.stdout).replace(/\n/g, "<br>");
        //stdout = stdout.replace(/\s/g, "&nbsp;");
        $('#accordion2').removeClass('hide');
        $("#job_logs").text("Logs...");
        $("#log_info").text(data.error);
        $("#job_info_outer").removeClass('hide');
        $("#job_info").text($('<div/>').text(data.stdout).html());
        paginator(30);
        percent = 100;
        $(".action_btn").show();
        $("#kill_job").hide();
        $(".bar").css("width", percent+"%");
    }, "json");

}

<%
  arguments = ''
  if result.get("arguments"):
    for arg in result["arguments"].split("\t"):
      arguments += '\'' + arg + '\','
  endif
%>


$(document).ready(function(){

  $("#help").popover({
    title: "${'Did you know?'}" +'<i class="icon-remove"></i>',
    content: $("#help-content").html(),
    html: true,
    delay: { hide: 500 },
    placement: 'bottom'
  });

  $('.script_label').tooltip({
    placement: 'bottom',
    title: 'Toggle editor',
    delay: 200
  });

  $(document).on('click','.popover i',function () {
    $("#help").popover('hide');
  })

  % if result.get("job_id") and result.get("JOB_SUBMITTED"):
  percent = 10;
  ping_job("${result['job_id']}");
  % endif

  $(".pigArgument").tagsManager({
    prefilled: [${arguments|n}],
    separateHiddenName: 'pigParams',
    hiddenTagListId:'fakeArgs',
    tagClass: 'pigArg',
    delimiters:[9,13],
    tagCloseIcon:'<i class="icon-remove-circle"></i>',
    onAdd: function  () {
      $("#save_button").removeAttr("disabled");
    }
  });

  $("#pig_script_form").validate({
    rules:{
      title:{
      required: true,
      % if not result.get("id"):
      remote: "${url("check_script_title")}"
      % endif
      },
      pig_script: "required",
    },
    messages: {
      title:{
      remote: "Script title already exists"
      }
    },
    highlight: function(label) {
        $(label).closest('.control-group').removeClass('success').addClass('error');
    },
    success: function(label) {
        label.text('OK!').addClass('valid')
          .closest('.control-group').removeClass('error').addClass('success');
    }
  });
  
  $(".action_btn").live("click", function(e){
    $("#operation_type").attr("name", $(this).attr("id"));
    $("#operation_type").val(1);
    $("#failure_info").addClass('hide');
    call_popup_var_edit($(this)).done(function() {
      $("#job_info_outer").removeClass('hide').html('<pre id="job_info"></pre>');
      $(".bar").attr("class", "bar");
      if (!$("#pig_script_form").valid()) return false;
      $(".action_btn").hide();
      $("#spinner").removeClass('hide');
      percent = 0;
      $(".bar").css("width", percent+"%");
      pig_editor.save();
      python_editor.save();
      $.ajax({
          url: "${url("start_job")}",
          dataType: "json",
          type: "POST",
          data: $("#pig_script_form").serialize(),
          success: function(data){
              $("#spinner").addClass('hide');
              $("#kill_job").show();
              $("#job_info_outer").removeClass('hide').prepend(data.text);
              job_id = data.job_id;
              ping_job(job_id);
          },
          error: function (xhr, ajaxOptions, thrownError) {
              $("#failure_info").removeClass('hide').html(xhr.responseText);
          }
      });
    });
  });
});

</script>

${commonfooter(messages)| n,unicode}
