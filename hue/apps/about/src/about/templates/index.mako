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
<%!
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
from about import conf
%>
${commonheader(_('About ' + page_title), "about", user, "100px")| n,unicode}

        % if user.is_superuser:
	<div class="subnav subnav-fixed">
		<div class="container-fluid">
		<ul class="nav nav-pills">
			<li><a href="${url("desktop.views.dump_config")}">${_('Configuration')}</a></li>
			<li><a href="${url("desktop.views.check_config")}">${_('Check for misconfiguration')}</a></li>
			<li><a href="${url("desktop.views.log_view")}">${_('Server Logs')}</a></li>
		</ul>
		</div>
	</div>
        % endif

	<div class="container-fluid">
		<h1 id="describe-header">${hue_title}</h1>

		<div id="update-tutorials-spinner"><h1>Updating tutorials...&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
		<h3 id="update-tutorials-msg"></h3>

        <div id="start-ambari-spinner"><h1><span id="start-ambari-caption">Enabling Ambari...</span>&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
        <h3 id="start-ambari-msg"></h3>

        % if about_top_html:
        <div class="alert">
            ${about_top_html| n,unicode}
        </div>
        % endif
		<div class="span-3">
			<div class="well sidebar-nav">
				<ul class="nav nav-list">
					<img src="/about/static/art/hortonworks_logo.png"/>
                                % if conf.TUTORIALS_INSTALLED.get():
		      		<li><a href="https://www.surveymonkey.com/s/Sandbox_Feedback">Leave Feedback</a></li>
                                % endif
				</ul>
			</div>
		</div>
		<div class="components span-9">
			<table class="table table-bordered">
			<thead>
    		<tr>
      			<th>Component</th>
      			<th colspan="2">Version</th>
    		</tr>
			</thead>
			<tbody>
			  % for component, version in components:
    			  <tr>
      			    <td>${component}</td>
                    % if conf.SANDBOX.get():
## Tutorials updater
                                % if component == 'Tutorials':
                                <td><div id="${component}">${version}</div></td>
                        <td><a href="#" class="btn"
                        id="updateTutorialsBtn">Update</a></td>

## Ambari switcher
                                % elif component == 'Ambari':
                                <td><div id="${component}">${version}</div></td>
                        <td><a href="#" class="btn"
                        id="startAmbariBtn">
                        % if not ambari_status:
                            Enable
                        % else:
                            Disable
                        % endif
                        </a></td>
                                % else:
                        <td colspan="2"><div id="${component}">${version}</div></td>
                                % endif
                    % else:
                        <td colspan="2"><div id="${component}">${version}</div></td>
                    % endif
    			  </tr>
			  % endfor
			</tbody>
			</table>
		</div>
        <div class="footer">
            <div class="container-fluid">
                <div class="logo">
                    <img src="/about/static/art/hortonworks_logo_bw.png"/>
                </div> 
                <div class="copyright">
                    <p class="pull-right">
                        Copyright © 2013 The Apache Software Foundation.
                        <br>
                        Apache Hadoop, Hadoop, HDFS, HBase, Hive, Mahout, Pig, Zookeeper are trademarks of the Apache Software Foundation.
                        <br>
                        Hue and the Hue logo are trademarks of Cloudera, Inc. and licensed under the Apache 2 license. For more information: 
                        gethue.com 
                    </p>
                </div>
            </div>
        </div>
    </div>


<style>
	#update-tutorials-spinner {
		display:none;
	}
    #start-ambari-spinner {
        display:none;
    }
    .logo {
        float: left;
        height: 78px;
        width: 140px;
    }
    .copyright {
        text-align: right;
        font-size: 11px;
        margin-top: 10px;
    }
    .components {
        margin-bottom: 65px;
    }
</style>

<script type="text/javascript" charset="utf-8">
## Tutorials update

    function showTutorialsError(msg){
        $('#update-tutorials-msg').html(msg);
        $('#update-tutorials-spinner').hide();
        $('#describe-header').show();
        $('#update-tutorials-msg').show();
    }
	$(document).ready(function(){
        $("#updateTutorialsBtn").click(function(){
            $('#describe-header').hide();
            $('#update-tutorials-spinner').show();
            $.post("${url("about.views.index")}", function(data){
            if(data.error != ""){
                    showTutorialsError("Update tutorials failed: " + data.error);
                }
            else {
                var curVersion = $("#Tutorials").text();
                if (data.tutorials != curVersion) {
                    showTutorialsError("Tutorials were successfully updated to " + data.tutorials + " version");
                    window.location.reload(true);
                }
                else{
                    showTutorialsError("There are no available tutorial updates");
                }
            }

            }, "json")
             .fail(function(jqXHR, exception) {
                if (jqXHR.status === 0) {
                    showTutorialsError("Update tutorials failed: you are offline. Please check your network.");
                } else if (jqXHR.status == 404) {
                    showTutorialsError("Update tutorials failed: requested page not found." + jqXHR.uri);
                } else if (jqXHR.status == 500) {
                    showTutorialsError("Update tutorials failed: internal server error.");
                } else if (exception === 'parsererror') {
                    showTutorialsError("Update tutorials failed: requested JSON parse failed.");
                } else if (exception === 'timeout') {
                    showTutorialsError("Update tutorials failed: time out error.");
                } else if (exception === 'abort') {
                    showTutorialsError("Update tutorials failed: ajax request aborted.");
                } else {
                    showTutorialsError("Update tutorials failed: unknown error.");
                }
            });
      });


## Ambari switch
    function showAmbariError(msg){
        $('#start-ambari-msg').html(msg);
        $('#start-ambari-spinner').hide();
        $('#describe-header').show();
        $('#start-ambari-msg').show();
    }
        var ambariCaption = ""
        $("#startAmbariBtn").click(function(){
            $("#startAmbariBtn").attr('disabled', true);
            $('#describe-header').hide();
            var url = "";
            var next_state = "";
            if ($("#startAmbariBtn").text().trim() == 'Enable') {
                ambariCaption = "Enabling Ambari";
                url = "${url("about.views.ambari", "Enable")}";
                next_state = "Disable";
            } else {
                ambariCaption = "Disabling Ambari";
                url = "${url("about.views.ambari", "Disable")}";
                next_state = "Enable";
            }
            console.log(ambariCaption);
            $('#start-ambari-caption').text(ambariCaption + "...");

            $('#start-ambari-spinner').show();
            $.post(url, function(data){
                if(data.error != ""){
                    showAmbariError(ambariCaption + " failed: " + data.error);
                }
                else {
                    showAmbariError("Ambari " + $("#startAmbariBtn").text().toLowerCase().trim() + "d successfully");
                    $("#startAmbariBtn").text(next_state);
                }
                $("#startAmbariBtn").attr('disabled', false);
            }, "json")
             .fail(function(jqXHR, exception) {
                if (jqXHR.status === 0) {
                    showAmbariError(ambariCaption + " failed: you are offline. Please check your network.");
                } else if (jqXHR.status == 404) {
                    showAmbariError(ambariCaption + " failed: requested page not found." + jqXHR.uri);
                } else if (jqXHR.status == 500) {
                    showAmbariError(ambariCaption + " failed: internal server error.");
                } else if (exception === 'parsererror') {
                    showAmbariError(ambariCaption + " failed: requested JSON parse failed.");
                } else if (exception === 'timeout') {
                    showAmbariError(ambariCaption + " failed: time out error.");
                } else if (exception === 'abort') {
                    showAmbariError(ambariCaption + " failed: ajax request aborted.");
                } else {
                    showAmbariError(ambariCaption + " failed: unknown error.");
                }
            });
      });
    });
</script>

${commonfooter(messages)| n,unicode}
