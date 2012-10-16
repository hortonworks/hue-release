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

${commonheader("Pig", "pig", user, "100px")}
${shared.menubar(section='My Scripts')}

<%!
from pig.models import PigScript, UDF
from pig.forms import UDFForm
udf_form = UDFForm()
udfs = UDF.objects.all()
pig_scripts = PigScript.objects.filter(saved=True).all()
%>

## Use double hashes for a mako template comment
## Main body
<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3" style="float: left;">
      <div class="well sidebar-nav">
        <h2>My scripts</h2>
	<ul class="nav nav-list">
          % for v in pig_scripts:
          <li>
      	    <p>
              <a href="${url('pig.views.delete', v.id)}">
                <img src="/pig/static/art/delete.gif" alt="Delete" height="12" width="12">
              </a>
              <a href="${url('pig.views.script_clone', v.id)}">
	        <img src="/pig/static/art/clone.png" alt="Delete" height="14" width="14">
	      </a>
	      <a href="${url('pig.views.index', obj_id=v.id)}">
	        % if v.title: 
	        ${v.title}
                % else:
                no title
                % endif
              </a>&nbsp;&nbsp;
	    </p>
          </li>
          % endfor
	</ul>
        <a class="btn" href="${url('root_pig')}">New script</a>
        <h2>Settings</h2>
	<ul class="nav nav-list">
	  <li>Limit dump:</li>
	  <li>
            <input class="inptext" type="text" placeholder="limit dump" />
	  </li>
	  <li>Email notification:</li>
	  <li>
	    <input class="email" type="checkbox" />
	  </li>
	  <li  class="nav-header"><a id="displayText" href='#'>User-defined Functions</a></li>
	  <div id="toggleText" style="display: none">
	    % for udf in udfs:
	    <li>
	      <a class="udf_register" href="#" value="${udf.url}">${udf.file_name}</a>
	    </li>
            % endfor
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
	  <form action="#" method="post" id="pig_script_form">
            <input type="hidden" name="script_id"  value="${result.get('script_id','')}" >
            <label for="id_title">Title:</label>
            <input id="id_title" type="text" name="title"
                   maxlength="200" value="${result.get('title',"")}">
            <label for="id_text">Pig script:</label>
            <textarea id="id_pig_script" rows="10" cols="40" name="pig_script">${result.get("pig_script", "")}</textarea>
            <div class="nav-collapse">
              <ul class="nav">
                <li class="dropdown">
                  <a data-toggle="dropdown" class="dropdown-toggle" href="#">
                    PIG helper<b class="caret"></b>
                  </a>
                  <ul class="dropdown-menu">
                    <li class="dropdown-submenu">
                      <a href="#">Aggregation functions</a>
                      <ul class="dropdown-menu">
                        <li><a href="#">AVG</a></li>
                        <li><a href="#">SUM</a></li>
                        <li><a href="#">MAX</a></li>
                        <li><a href="#">MIN</a></li>
                        <li><a href="#">CLUSTERED</a></li>
                      </ul>
                    </li>
                    <li class="dropdown-submenu">
                      <a href="#">HCatalog</a>
                      <ul class="dropdown-menu">
                        <li><a href="#">A = LOAD '__' USING org.apache.hcatalog.pig.HCatLoader();</a></li>
                      </ul>
                    </li>
                    <li class="dropdown-submenu">
                      <a href="#">Python UDF</a>
                      <ul class="dropdown-menu">
                        <li><a href="#">Register python_udf.py' using jython as myfuncs;</a></li>
                      </ul>
                    </li>
                  </ul>
            </div>
            % if result.get("python_script"):
            <label>Python UDF</label>
                 <textarea id="python_code" name="python_script"
                           rows="4" name="python_text">
                   ${result['python_script']}
            </textarea>
            % else:
            <div style="display:none;">
                 <label>Python UDF</label>
                 <textarea id="python_code" name="python_script" rows="4"></textarea>
            </div>
            % endif
	<input type="hidden" name="limit" class='intolimit' />
	<input type="hidden" name="email" class='intoemail' />
	<div class="actions">
	  <input class="btn primary" type="submit" name="submit" value="Save" />
	  <input class="btn primary" type="submit" name="submit" value="Execute" />
	  <input class="btn primary" type="submit" name="submit" value="Explain" />
	  <input class="btn primary" type="submit" name="submit" value="Describe" />
	  <input class="btn primary" type="submit" name="submit" value="Dump" />
	  <input class="btn primary" type="submit" name="submit" value="Illustrate" />
	  <input class="btn primary" type="button" id="start_job" name="submit" value="Schedule" />
          <input class="btn primary" type="button" id="kill_job"  value="Kill job" style="display:none" />
	</div>
	</form>
      </div>
      <div class="div_conteiner">
        <div class="progress progress-striped active">
          <div class="bar" style="width: 0%;"></div>
        </div>
        
        <div class="alert alert-success" id="job_info">
          % if 'stdout' in result:
          ${result['stdout']}
          % endif
        </div>
        
        <div class="alert alert-error" id="failure_info">
        </div>
        
        <div class="accordion alert alert-warning" id="accordion2">
          <div class="accordion-group">
            <div class="accordion-heading">
              <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#collapseOne">
                Logs...
              </a>
            </div>
            <div id="collapseOne" class="accordion-body collapse in">
              <div class="accordion-inner" id="log_info">
                % if 'error' in result:
                ${result['error']}
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
<script src="/pig/static/js/codemirror.js"></script>
<script src="/pig/static/js/pig.js"></script>
<script src="/pig/static/js/python.js"></script>
<script src="/pig/static/js/pig_scripts.js"></script>
<script type="text/javascript">
var percent = 0;
function get_job_result(job_id)
{
    $.post("${url("get_job_result")}", {job_id: job_id}, function(data){
        if (data.error==="" && data.stdout==="" && data.exit==="")
        {
            get_job_res_timer = window.setTimeout("get_job_result('"+job_id+"');", 3000);
            return;
        }
        $("#log_info").html(data.error);
        $("#job_info").append("<br>"+data.stdout.replace("\n", "<br>"));
        percent = 100;
        $("#start_job").show();
        $("#kill_job").hide();
        $(".bar").css("width", percent+"%");
    }, "json");
    
}

function ping_job(job_id){
    var url = '/proxy/localhost/50111/templeton/v1/queue/';          
    $.get(url+job_id+'?user.name=hdfs', 
          function(data) {
              if (data.status.jobComplete)
              {
                  if (data.status.failureInfo != 'NA')
                      $("#failure_info").html(data.status.failureInfo);
                  percent += 10;
                  $(".bar").css("width", percent+"%");
                  get_job_res_timer = window.setTimeout("get_job_result('"+job_id+"');", 8000);
                  return 
              }
              if (/[1-9]\d?0?\%/.test(data.percentComplete))
              {
                  var job_done = parseInt(data.percentComplete.match(/\d+/)[0]);
                  percent = (job_done < percent)?percent:job_done;              
                  $(".bar").css("width", percent + "%");
              }
              else
              {
                  percent += 1;
                  $(".bar").css("width", percent+"%");
              }
              ping_job_timer = window.setTimeout("ping_job('"+job_id+"');", 1000);     
           });
          
}


$(document).ready(function(){


var get_job_res_timer = null;
var ping_job_timer = null;

var job_id = null;
    
    $(".collapse").collapse();
    
    $("#kill_job").live('click', function(){
        clearTimeout(get_job_res_timer);
        clearTimeout(ping_job_timer);
        $(this).hide();
        $("#id_text").removeAttr("disabled");
        $("#start_job").show();
        percent = 0;
        $(".bar").css("width", percent+"%");
        $.post("${url("kill_job")}",{job_id: job_id}, function(data){
            $("#job_info").append("<br>"+data.text);
        }, "json");
    });
    
    
    $("#start_job").live("click", function(){
        $(this).hide();              
        $("#id_text").attr("disabled", "disabled");
        percent = 2;
        $(".bar").css("width", percent+"%");
        $.ajax({
            url: "${url("start_job")}",
            dataType: "json",
            type: "POST",
            data: $("#pig_script_form").serialize()+"&pig_script="+escape(pig_editor.getValue()),
            success: function(data){
                $("#kill_job").show();
                $("#job_info").append(data.text);
                job_id = data.job_id;
                ping_job(job_id);
            }
        });
    });
});

</script>

${commonfooter()}
