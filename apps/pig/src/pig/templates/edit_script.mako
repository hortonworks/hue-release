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
${commonheader("Pig", "pig", user, "100px")}
${shared.menubar(section='My Scripts')}

<%!
from pig.models import UDF
from pig.forms import UDFForm
udf_form = UDFForm()
udfs = UDF.objects.all()
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
            <a id="displayText" href='javascript:void(0);'>User-defined Functions</a>
          </li>
	  <div id="toggleText" style="display: none">
	  ${my_scripts.udfs(result['udfs'])}
	  </div>
	  <li>
	    <form id="udfs" enctype="multipart/form-data" action="${url('pig.views.piggybank')}" method="post">
    	      ${udf_form}
      	      <input class="btn" type="submit" name="submit" value="Add" />
	    </form>
          </li>
	</ul>
      </div>
    </div>
    <div class="span9" style="float: left; width: 70%;">
      <div class="clearfix">
        <div class="input">
	  <form action="${url("root_pig")}" method="post" id="pig_script_form">
            <input type="hidden" name="script_id"  value="${result.get('id','')}" >
            <label for="id_title">Title:</label>
            <div class="control-group">
            <label for="id_text">Pig script:</label>
              <div class="controls">
                <input id="id_title" type="text" name="title" required="required"
                       maxlength="200" value="${result.get('title',"")}">
              </div>
            </div>
            <textarea id="id_pig_script" required="required" rows="10" cols="40" name="pig_script">${result.get("pig_script", "")}</textarea>
            <div class="nav-collapse">
              <ul class="nav">
                <li class="dropdown">
                  <a data-toggle="dropdown" class="dropdown-toggle" href="#">
                    PIG helper<b class="caret"></b>
                  </a>
                  <ul class="dropdown-menu" id="pig_helper">
                    <li class="dropdown-submenu">
                      <a href="#">Aggregation functions</a>
                      <ul class="dropdown-menu">
                        <li><a href="#">AVG(%VAR%)</a></li>
                        <li><a href="#">SUM(%VAR%)</a></li>
                        <li><a href="#">MAX(%VAR%)</a></li>
                        <li><a href="#">MIN(%VAR%)</a></li>
                        <li><a href="#">COUNT(%VAR%)</a></li>

                      </ul>
                    </li>
                    <li class="dropdown-submenu">
                      <a href="#">Data processing functions</a>
                      <ul class="dropdown-menu">
                        <li><a href="#">FOREACH %DATA% GENERATE %NEW_DATA%</a></li>
                        <li><a href="#">FILTER %VAR% BY %COND%</a></li>
                        <li><a href="#">GROUP %VAR% BY %VAR%</a></li>
                        <li><a href="#">COGROUP %VAR% BY %VAR%</a></li>
                        <li><a href="#">JOIN %VAR% BY </a></li>
                        <li><a href="#">LIMIT</a></li>
                      </ul>
                    </li>

                    <li class="dropdown-submenu">
                      <a href="#">I/0</a>
                      <ul class="dropdown-menu">
                        <li><a href="#">A = LOAD '%FILE%';</a></li>
                        <li><a href="#">DUMP %VAR%;</a></li>
                        <li><a href="#">STORE %VAR% INTO %PATH%;</a></li>
                      </ul>
                    </li>
                    <li class="dropdown-submenu">
                      <a href="#">Debug</a>
                      <ul class="dropdown-menu">
                        <li><a href="#">EXPLAIN %VAR%;</a></li>
                        <li><a href="#">ILLUSTRATE %VAR%;</a></li>
                        <li><a href="#">DESCRIBE %VAR%;</a></li>
                      </ul>
                    </li>
                    <li class="dropdown-submenu">
                      <a href="#">HCatalog</a>
                      <ul class="dropdown-menu">
                        <li><a href="#">A = LOAD '%TABLE%' USING org.apache.hcatalog.pig.HCatLoader();</a></li>
                      </ul>
                    </li>
                    <li class="dropdown-submenu">
                      <a href="#">Python UDF</a>
                      <ul class="dropdown-menu">
                        <li>
                          <a href="#" data-python="true">REGISTER 'python_udf.py' USING jython AS myfuncs;
                          </a>
                        </li>
                      </ul>
                    </li>
                  </ul>
            </div>
            % if result.get("python_script"):
            <label>Python UDF</label>
                 <textarea id="python_code" name="python_script"
                           rows="4" >${result['python_script']}</textarea>
            % else:
            <div style="display:none;" id="python_textarea">
                 <label>Python UDF</label>
                 <textarea id="python_code" name="python_script"></textarea>
            </div>
            % endif
	<input type="hidden" name="email" class='intoemail' />
	<div class="actions">
	  <input class="btn primary" type="submit" name="submit_action" id="save_button"
                 value="Save"
                 % if result.get("id"):
                 disabled="disabled"
                 % endif
                 />
	  <input class="btn primary" type="button" id="start_job" name="submit_action"
	  value="Execute" />
          <input class="btn primary" type="button" id="kill_job"  value="Kill job" style="display:none" />
	  <input class="btn primary explain" type="button"
                 id="explain" name="submit_action" value="Explain" />
	  <input class="btn primary explain" name="submit_action" type="button" id="check" value="Syntax check" />
	</div>
	</form>
      </div>
      <div class="div_conteiner">
        <div class="progress progress-striped active">
          <div class="bar" style="width: 0%;"></div>
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
          ${result['stdout']}
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
              <div class="accordion-inner" id="log_info">
                % if 'error' in result:
                ${result['error'].replace("\n", "<br>")}
                % endif
              </div>
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
</style>
<script type="text/javascript" src="http://ajax.aspnetcdn.com/ajax/jquery.validate/1.9/jquery.validate.min.js">
</script>
<script src="/pig/static/js/codemirror.js"></script>
<script src="/pig/static/js/pig.js"></script>
<script src="/pig/static/js/python.js"></script>
<script src="/pig/static/js/simple-hint.js"></script>
<script src="/pig/static/js/pig-hint.js"></script>
<script src="/pig/static/js/jquery.pagination.js"></script>
<script src="/pig/static/js/searchcursor.js"></script>
<script src="/pig/static/js/match-highlighter.js"></script>
<script src="/pig/static/js/emacs.js"></script>
<script src="/pig/static/js/pig_scripts.js"></script>
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
        var stdout = data.stdout.replace(/\n/g, "<br>");
        stdout = stdout.replace(/\s/g, "&nbsp;");
        $("#job_logs").text("Logs...");
        $("#log_info").html(data.error.replace(/\n/g, "<br>"));
        $("#job_info").html(data.stdout);
        paginator(30);
        percent = 100;
        $("#start_job").show();
        $("#kill_job").hide();
        $(".bar").css("width", percent+"%");
    }, "json");

}



$(document).ready(function(){

    $('.explain').live("click", function(e){
      call_popup_var_edit().done(function() {
        if (!$("#pig_script_form").valid()) return false;
        explain_progres(0);
        $("#id_text, .explain, #start_job, #kill_job").attr("disabled", "disabled");
        percent = 2;
        $(".bar").css("width", percent+"%");
	var t_s = $(this).attr('value')
        pig_editor.save();
        python_editor.save();
        $.ajax({
            url: "${url('explain')}?t_s=" + t_s,
            dataType: "json",
            type: "POST",
            data: $("#pig_script_form").serialize(),
            success: function(data){
                $("#job_info").text('');
                $("#job_info").append(data.text);
                $("#id_text, .explain, #start_job, #kill_job").removeAttr("disabled");
            }
        });

});
            });

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

    $("#kill_job").live('click', function(){
        clearTimeout(globalTimer);
        $(this).hide();
        $("#id_text").removeAttr("disabled");
        $("#start_job").show();
        percent = 0;
        $(".bar").css("width", percent+"%");
        $.post("${url("kill_job")}",{job_id: job_id}, function(data){
            $("#job_info").append("<br>"+data.text);
        }, "json");
    });


    $("#start_job").live("click", function(e){
call_popup_var_edit().done(function() {
        $("#job_info_outer").html('<pre id="job_info"></pre>');
        $(".bar").attr("class", "bar");
        if (!$("#pig_script_form").valid()) return false;
        $("#start_job").hide();
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
            }
        });
       });

    });
});

</script>

${commonfooter()}
