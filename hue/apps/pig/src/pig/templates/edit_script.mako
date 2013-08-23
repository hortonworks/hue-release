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
<%namespace name="shared" file="shared_components.mako" />
<%namespace name="my_scripts" file="my_scripts.mako" />
${commonheader("Pig", "pig", user, "100px")| n,unicode}
${shared.menubar(section='My Scripts')}

<%!
from pig.models import UDF
from pig import conf
udfs = UDF.objects.all()
UDF_PATH = conf.UDF_PATH.get()
%>

## Use double hashes for a mako template comment
## Main body
<div id="show-modal-for-var" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>Please specify parameters for this variable(s):</h3>
    </div>
    <div class="modal-body">
        <div class="clearfix">
           <div class="modal-for-var-input-warp">

           </div>
        </div>
    </div>
    <div class="modal-footer">
        <button id="save-values-for-var" class="btn primary">Save</button>
    </div>
</div>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3" style="float: left;">
      <div class="well sidebar-nav">
        ${my_scripts.my_scripts(result['scripts'])}

        <h2>Settings</h2>
          <ul class="nav nav-list">
            <li>Email notification:</li>
            <li>
              <input class="email" type="checkbox"
                   % if result.get("email_notification"):
                   checked="checked"
                   % endif
                   />
            </li>
            <li  class="nav-header">
              <div class="accordion" id="accordion3" >
                <div class="accordion-group">
                  <div class="accordion-heading">
                    <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion3" href="#collapseOne2">
                      User-defined Functions <i class="icon-chevron-down"></i>
                    </a>
                  </div>
                  <div id="collapseOne2" class="accordion-body in collapse"
                       style="height: auto; text-transform:none;">
                    <div class="accordion-inner">
                       ${my_scripts.udfs(result['udfs'])}
                    </div>
                  </div>
                </div>

              </div>

            </li>
            <li>
              <form id="udfs_form" enctype="multipart/form-data"
                  action="${url('pig.views.udf_create')}"
                  method="post" data-destination="${UDF_PATH}"> ${ csrf_token_field | n } 
                  <div id="udf_file_upload"><i class="icon-upload icon-white"></i> Upload UDF jar</div>                
              </form>
            </li>
          </ul>
      </div>
    </div>
    <div class="span9" style="float: left; width: 70%;">
      <div class="clearfix">
        <div class="input">
            <form action="${url("root_pig")}" method="post" id="pig_script_form"> ${ csrf_token_field | n } 
            <input type="hidden" name="script_id"  value="${result.get('id','')}" >
            <label for="id_title">Title:</label>
            <div class="control-group">

              <div class="controls">
                <input id="id_title" type="text" name="title" required="required"
                       maxlength="200" value="${result.get('title',"")}">
              </div>
            </div>            
           
            <%include file="pig_helper.html" />
            
            <label for="id_pig_script" >Pig script:
              <div >
              <a href="javascript:void(0);" class="alert-success" ><i class="icon-question-sign" id="help"></i></a>
              
              <div id="help-content" class="hide">
                <ul>
                  <li class="text-success">Press ctrl+space for autocompletion</li>
                  <li class="text-success">To see table fields helper type table_name + "." (e.g. sample_07.)</li>
                </ul>
              </div>
              
            </div>  
            </label>
            
            
            <textarea id="id_pig_script" required="required" rows="10" cols="40" name="pig_script">${result.get("pig_script", "")}</textarea>
            % if result.get("python_script"):
            <div id="python_textarea">
              <label class="script_label" for="python_code">Python UDF:</label>
              <textarea id="python_code" name="python_script" rows="4" >${result['python_script']}</textarea>
            </div>
            % else:
            <div id="python_textarea"style="display:none;" >
              <label class="script_label" for="python_code">Python UDF:</label>
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
	            <input class="btn primary action_btn" type="button" id="start_job" name="submit_action"value="Execute" />
              <input class="btn primary " type="button"id="kill_job"  value="Kill job" style="display:none" />
	            <input class="btn primary action_btn" type="button"id="explain" name="submit_action" value="Explain" />
	            <input class="btn primary action_btn" name="submit_action"type="button" value="Syntax check" id="syntax_check" />
	          </div>
	        </form>
          <input type="hidden" id="fakeArgs">
        </div>

        <a class="btn-success btn-mini"
           % if 'stdout' in result and 'job_id' in result:
           href="${url("download_job_result", job_id=result['job_id'])}"
           % else:
           style="display:none;"
           % endif
           id="download_job_result">
          <i class="icon-download-alt"></i></a>


        <div class="alert alert-success" id="job_info_outer">
          <pre id="job_info">
          % if 'stdout' in result:
${result['stdout']|h}
          % endif
          </pre>
        </div>

        <div class="alert alert-error" id="failure_info">
        </div>

        <div class="accordion alert alert-warning" id="accordion2">
          <div class="accordion-group">
            <div class="accordion-heading">
              <a class="accordion-toggle" data-toggle="collapse" id="job_logs"
          data-parent="#accordion2" href="#collapseOne">
                % if 'error' in result:
                Logs...
                % endif
              </a>
            </div>
            <div id="collapseOne" class="accordion-body collapse in">
              <pre class="accordion-inner" id="log_info">
                % if 'error' in result:
${result['error']}
                % endif
              </pre>
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
<style type="text/css" media="screen">
  .CodeMirror-focused span.CodeMirror-matchhighlight {
background:  #e7e4ff; !important; }
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
.CodeMirror {
  border: 2px solid #eee;
}
#pigArguments .help-inline {
  margin-right: 5px;
}
#pigArguments > div {


</style>
<script type="text/javascript" src="/pig/static/js/jquery.validate.min.js"></script>
<script src="/pig/static/js/codemirror.js"></script>
<script src="/pig/static/js/pig.js"></script>
<script src="/pig/static/js/python.js"></script>
<script src="/pig/static/js/simple-hint.js"></script>
<script src="/pig/static/js/show-hint.js"></script>
<script src="/pig/static/js/pig-hint.js"></script>
<script src="/pig/static/js/jquery.pagination.js"></script>
<script src="/pig/static/js/searchcursor.js"></script>
<script src="/pig/static/js/match-highlighter.js"></script>
<script src="/pig/static/js/emacs.js"></script>
<script src="/pig/static/js/pig_scripts.js"></script>
<script src="/pig/static/js/bootstrap-fileupload.min.js"></script>
<script type="text/javascript">
var percent = 0;
var globalTimer = null;
var job_id = null;

function get_job_result(job_id)
{
    $.post("${url("get_job_result")}", {job_id: job_id}, function(data){
        if (data.error==="" && data.stdout==="")
        {
            globalTimer = window.setTimeout("get_job_result('"+job_id+"');", 3000);
            percent += 1;
            $(".bar").css("width", percent+"%");
            return;
        }

        if (parseInt(data.exit)==0) $(".bar").addClass("bar-success");
        else $(".bar").addClass("bar-danger");

        $("#download_job_result").show();
        $("#download_job_result").attr("href", "/pig/download_job_result/" +
                                       job_id + "/");
        //var stdout = escape(data.stdout).replace(/\n/g, "<br>");
        //stdout = stdout.replace(/\s/g, "&nbsp;");
        $("#job_logs").text("Logs...");
        $("#log_info").text(data.error);
        $("#job_info").text($('<div/>').text(data.stdout).html());
        paginator(30);
        percent = 100;
        $(".action_btn").show();
        $("#kill_job").hide();
        $(".bar").css("width", percent+"%");
    }, "json");

}



$(document).ready(function(){
$("#help").popover({'title': "${'Did you know?'}", 'content': $("#help-content").html(), 'html': true, delay: { hide: 500 }});
% if result.get("job_id") and result.get("JOB_SUBMITED"):
percent = 10;
ping_job("${result['job_id']}");
% endif

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
}},
highlight: function(label) {
    $(label).closest('.control-group').addClass('error');
  },
success: function(label) {
    label
      .text('OK!').addClass('valid')
      .closest('.control-group').addClass('success');
  }
});


    $(".collapse").collapse();



    $(".action_btn").live("click", function(e){
$("#operation_type").attr("name", $(this).attr("id"));
$("#operation_type").val(1);
call_popup_var_edit($(this)).done(function() {
        $("#job_info_outer").html('<pre id="job_info"></pre>');
        $(".bar").attr("class", "bar");
        if (!$("#pig_script_form").valid()) return false;
        $(".action_btn").hide();
        percent = 0;
        $(".bar").css("width", percent+"%");
        pig_editor.save();
        python_editor.save()
        $.ajax({
            url: "${url("start_job")}",
            dataType: "json",
            type: "POST",
            data: $("#pig_script_form").serialize(),
            success: function(data){
                $("#kill_job").show();
                $("#job_info_outer").prepend(data.text);
                job_id = data.job_id;
                ping_job(job_id);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                $("#failure_info").html(xhr.responseText);
            }
        });
       });

    });
});

</script>

${commonfooter(messages)| n,unicode}
