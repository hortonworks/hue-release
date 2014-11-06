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
%>

<%namespace name="layout" file="layout.mako" />
<%namespace name="util" file="util.mako" />

${ commonheader(_('Waiting for query...'), app_name, user, '100px') | n,unicode }

<style>
	.ri_header {
		display: inline;
		font-size: 14px;

	}
</style>


${layout.menubar(section='query')}

## Required for unit tests
<!-- <meta http-equiv="refresh" content="3;${url(app_name + ':watch_query', query.id)}?${fwd_params}" /> -->

<div class="container-fluid">
	<h1>${_('Waiting for query...')} ${util.render_query_context(query_context)}</h1>
  <div class="alert alert-error query_error" style="display: none;"><p></p></div>
	<div class="row-fluid">
		<div class="span3">
						<li class="nav">
							<div class="control-group">
								<button id="cancel-btn" class="btn btn-small" data-loading-text="${ _('Canceling...') }" rel="tooltip" data-placement="right" data-original-title="${ _('Cancel the query') }">
									${ _('Cancel') }
								</button>
							</div>
						</li>
			<div class="well sidebar-nav">
				<ul class="nav nav-list">
					<%
			          n_jobs = hadoop_jobs and len(hadoop_jobs) or 0
			          mr_jobs = (n_jobs == 1) and _('MR Job') or _('MR Jobs')
			        %>
				 	% if n_jobs > 0:
						<li id="jobsHeader" class="nav-header">${mr_jobs} (${n_jobs})</li>
						% for jobid in hadoop_jobs:
						    <li><a class="jobLink wordbreak" href="${url("jobbrowser.views.single_job", job=jobid)}">${jobid.replace("job_", "")}</a></li>
						% endfor
					% else:
						<li id="jobsHeader" class="nav-header">${mr_jobs}</li>
						<li class="jobLink wordbreak">${_('No Hadoop jobs were launched in running this query.')}</li>
					% endif
					<li class="nav-header">${_('Total Jobs to Run')| n,unicode}</li>
					<li id="total">&nbsp;</li>
					<li class="nav-header">${_('Job Running')| n,unicode}</li>
					<li id="runningJob">&nbsp;</li>
					<li class="nav-header">${_('User')}</li>
					<li id="user">&nbsp;</li>
					<li class="nav-header">${_('Status')}</li>
					<li id="jobStatus">&nbsp;</li>
					<li class="nav-header">${_('Maps:')}</li>
					<li id="jobMaps">&nbsp;</li>
					<li class="nav-header">${_('Reducers:')}</li>
					<li id="jobReduces">&nbsp;</li>
				</ul>
			</div>
		</div>
		<div class="span9">
			<ul class="nav nav-tabs">
				<li class="active"><a href="#log" data-toggle="tab">${_('Log')}</a></li>
				<li><a href="#query" data-toggle="tab">${_('Query')}</a></li>
			</ul>

		   	<div class="tab-content">
				<div class="active tab-pane" id="log">
					<pre>${ log }</pre>
				</div>
				<div class="tab-pane" id="query">
					<pre>${ query.get_current_statement() }</pre>
				</div>
			</div>
		</div>
	</div>
</div>

<script src="/jobbrowser/static/js/utils.js" type="text/javascript" charset="utf-8"></script>

<script>

  $(document).ready(function(){
    var fwdUrl = "${url(app_name + ':watch_query', query.id, download_format)}?${fwd_params}";
    var labels = {
      MRJOB: "${_('MR Job')}",
      MRJOBS: "${_('MR Jobs')}"
    }

    resizeLogs();
    refreshView();
    var logsAtEnd = true;

    function refreshView() {
      $.getJSON("${url('beeswax' + ':watch_query_refresh_json', query.id, download_format)}", function (data) {
        if (data.status == -1) {
          $('.query_error').show().prev().hide();
          $('.query_error p').html('<strong>'+ data['message'] + '</strong>');
          return false;
        }

        if (data.isSuccess || data.isFailure) {
          location.href = fwdUrl;
        }
        if (data.job )
        {
          updateStatus(data.job, data.total, data.current, data.jobs);
        }
        else{
          updateStatus(null, null, null, null);
        }


        if (data.jobs && data.jobs.length > 0) {
          $(".jobLink").remove();
          $("#jobsHeader").text((data.jobs.length > 1 ? labels.MRJOBS : labels.MRJOB) + " (" + data.jobs.length + ")");
          for (var i = 0; i < data.jobs.length; i++) {
            $("#jobsHeader").after($("<li>").addClass("jobLink wordbreak").html("<a href=\"" + data.jobUrls[data.jobs[i]] + "\">" + data.jobs[i].replace("job_", "") + "</a>"));
          }
        }
        var _logsEl = $("#log pre");
        var newLines = data.log.split("\n").slice(_logsEl.text().split("\n").length);
        _logsEl.text(_logsEl.text() + newLines.join("\n"));
        if (logsAtEnd) {
          _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
        }
        window.setTimeout(refreshView, 5000);
      });
    }

    $(window).resize(function () {
      resizeLogs();
    });

    $("a[href='#log']").on("shown", function () {
      resizeLogs();
    });

    $("#log pre").scroll(function () {
      if ($(this).scrollTop() + $(this).height() + 20 >= $(this)[0].scrollHeight) {
        logsAtEnd = true;
      }
      else {
        logsAtEnd = false;
      }
    });

    function resizeLogs() {
      $("#log pre").css("overflow", "auto").height($(window).height() - $("#log pre").position().top - 40);
    }

    $("#cancel-btn").click(function() {
      var _this = this;
      $(_this).button('loading');
      $.post("${ url(app_name + ':cancel_operation', query.id) }",
        function(response) {
          if (response['status'] != 0) {
            $.jHueNotify.error("${ _('Problem: ') }" + response['message']);
          } else {
            $.jHueNotify.info("${ _('Query canceled!') }")
          }
        }
      );
      return false;
    });

  });

	function updateStatus(job, total, current, jobs) {
		if (total){
		$("#total").html((total ? '<i title="${ _('Total Jobs to Run') }"></i> ' : '') + '<div class="ri_header">' +total + '</div>');
	}
	else{
		$("#total").html("${_('N/A')}");
	}

	if (current){
		$("#runningJob").html( (current ? '<i title="${ _('Running Job') }"></i> ' : '') + '<div class="ri_header">' +current + '</div>');
	}
	else{
		$("#runningJob").html("${_('N/A')}");
	}

	if (job && job.user){
		$("#user").html((job.user ? '<i title="${ _('User') }"></i> ' : '') + '<div class="ri_header">' + job.user + '</div>');
	}
	else{
		$("#user").html("${_('N/A')}");
	}
	if (job && jobs.length==current){
			$("#jobStatus").html('<span class="label ' + getStatusClass(job.status) + '">' + (job.isRetired && !job.isMR2 ? '<i class="icon-briefcase icon-white" title="${ _('Retired') }"></i> ' : '') + job.status + '</span>');
		}
		else if(job && jobs && current>jobs.length){
			$("#jobStatus").html("${_('Preparing Job: ')}" + (jobs.length+1));
		}
		else{
			$("#jobStatus").html("${_('N/A')}");
		}
		if (job && job.desiredMaps > 0 && jobs.length==current) {
			$("#jobMaps").html((job.isRetired ? '${_('N/A')}' : '<div class="progress" style="width:200px" title="' + (job.isMR2 ? job.mapsPercentComplete : job.finishedMaps + '/' + job.desiredMaps) + '"><div class="bar-label">' + job.finishedMaps + '/' + job.desiredMaps + '</div><div class="' + 'bar ' + getStatusClass(job.status, "bar-") + '" style="margin-top:-20px;width:' + job.mapsPercentComplete + '%"></div></div>'));
		}
		else {
			$("#jobMaps").html("${_('N/A')}");
		}
		if (job && job.desiredReduces > 0 && jobs.length==current) {
			$("#jobReduces").html((job.isRetired ? '${_('N/A')}' : '<div class="progress" style="width:200px" title="' + (job.isMR2 ? job.reducesPercentComplete : job.finishedReduces + '/' + job.desiredReduces) + '"><div class="bar-label">' + job.finishedReduces + '/' + job.desiredReduces + '</div><div class="' + 'bar ' + getStatusClass(job.status, "bar-") + '" style="margin-top:-20px;width:' + job.reducesPercentComplete + '%"></div></div>'));
		}
		else {
			$("#jobReduces").html("${_('N/A')}");
		}


	}

</script>


${ commonfooter(messages) | n,unicode }
