<%!
from django.utils.translation import ugettext as _
from desktop.views import commonheader, commonfooter 
from pig.models import Job
%>
<%namespace name="shared" file="shared_components.mako" />
<%namespace name="my_scripts" file="my_scripts.mako" />

${commonheader("Pig", "pig", user, "100px")| n,unicode}
${shared.menubar(section='Query history')}

## Use double hashes for a mako template comment
## Main body
<div class="span-5">
<table class="table table-bordered">
<thead>
    <tr>
      <th>Date</th>
      <th>Pig Script</th>
      <th>Status</th>
      <th>Logs</th>
      <th>Results</th>
      <th>Delete</th>
    </tr>
</thead>
<tbody>
% for job in jobs.object_list:
    <tr>
      <td><a href="${url("query_history_job_detail", job_id=job.job_id)}">${job.start_time.strftime('%d.%m.%Y %H:%M')}</a></td>
      <td
        % if job.status == job.JOB_SUBMITTED:
          class='running' data-jobid="${job.job_id}"
        % endif
        ><a class="show-script-link" href="#" data-jobid="${job.job_id}"> ${job.script_title}</a></td>
      <td>
          % if job.status == job.JOB_SUBMITTED:
          <span class="label label-warning">RUNNING</span>
          % elif job.status == job.JOB_FAILED:
          <span class="label label-important">FAILED</span>
           % elif job.status == job.JOB_KILLED:
          <span class="label label-important">KILLED</span>
          % else:
          <span class="label label-success">SUCCEEDED</span>
          % endif
      </td>
      <td><a href='#' class="show-logs-link" data-jobid="${job.job_id}"> Logs</a></td>
      <td>
        <a class="btn-success btn-mini" href="${url("download_job_result", job_id=job.job_id)}">
          <i class="icon-download-alt"></i>
        </a>&nbsp;
        <a href='#' class="show-results-link" data-jobid="${job.job_id}"> Results</a></td>
      <td><a class="confirm-delete-link" href="#" data-jobid="${job.job_id}"><i class="icon-trash"></i> Delete</a></td>
    </tr>
% endfor
</tbody>
</table>
<div class="pagination">
   <ul>
     % if jobs.has_previous():
     <li><a href="?page=${jobs.previous_page_number()}">previous</a></li>
     % endif
     <li class="active"><span>Page ${jobs.number } of ${jobs.paginator.num_pages}.</span></li>
     
     % if jobs.has_next():
     <li><a href="?page=${jobs.next_page_number()}">next</a></li>
     % endif
   </ul>
</div>
</div>


${my_scripts.modal({
  'windowId':'show-script-dialog',
  'title': 'Pig Script',
  'htmlbody': '<pre id="show-script-dialog-body"></pre>',
  'cBtnText':'Close',
  'cBtnClass':'btn',
  'cBtnAttr': 'data-dismiss="modal"',
  'cancelBtn': False,
})}

${my_scripts.modal({
  'windowId':'show-logs-dialog',
  'title': 'Logs',
  'htmlbody': '<pre id="show-logs-dialog-body"></pre>',
  'cBtnText':'Close',
  'cBtnClass':'btn',
  'cBtnAttr': 'data-dismiss="modal"',
  'cancelBtn': False,
})}

${my_scripts.modal({
  'windowId':'show-results-dialog',
  'title': 'Results',
  'htmlbody': '<pre id="show-results-dialog-body"></pre>',
  'cBtnText':'Close',
  'cBtnClass':'btn',
  'cBtnAttr': 'data-dismiss="modal"',
  'cancelBtn': False,
})}

${my_scripts.modal({
  'windowId':'confirm-delete-modal',
  'title': 'Confirm Delete',
  'textbody': 'Are you sure you want to delete job results?',
  'cBtnId': 'confirm-delete-btn',
  'cBtnText':'Delete',
  'cBtnClass':'btn btn-danger',
})}

<script type="text/javascript">
$(document).ready(function () {
  $('.table tbody').find('td.running').each(function (i,_td) {
    var td=_td;
    $.post('/pig/check_running_job/'+$(td).data('jobid')+'/', function (data) {
        var span = $(td).next().find('span');
        if (data.status==${Job.JOB_FAILED}) {
          span.attr('class','label label-important').text('FAILED');
        } else if (data.status==${Job.JOB_KILLED}) {
          span.attr('class','label label-important').text('KILLED');
        }
      },
    'json');
  });

  // show script in popup dialog
  $(document).on("click", ".show-script-link", function () {
    var job_id = $(this).data('jobid')
    $.post("${url("get_job_result_script")}", {job_id: job_id}, function(data) {
      if (data.pig_script === "") {
        $("#show-script-dialog-body").text("No script found");
      }
      else {
        $("#show-script-dialog-body").text(data.pig_script);
      }
    }, "json");
    $("#show-script-dialog").modal("show");
  });

  // show job logs in popup dialog
  $(document).on("click", ".show-logs-link", function () {
    var job_id = $(this).data('jobid')
    $.post("${url("get_job_result_stderr")}", {job_id: job_id}, function(data) {
      if (data.stderr === "") {
        $("#show-logs-dialog-body").text("No logs found");
      }
      else {
        $("#show-logs-dialog-body").text(data.stderr);
      }
    }, "json");
    $("#show-logs-dialog").modal("show");
  });

  // show job results in popup dialog
  $(document).on("click", ".show-results-link", function () {
    var job_id = $(this).data('jobid')
    $.post("${url("get_job_result_stdout")}", {job_id: job_id}, function(data) {
      if (data.stdout === "") {
        $("#show-results-dialog-body").text("No results found");
      }
      else {
        $("#show-results-dialog-body").text(data.stdout);
      }
    }, "json");
    $("#show-results-dialog").modal("show");
  });

  // delete job results
  $('.confirm-delete-link').on('click', function(e) {
    e.preventDefault();
    var job_id = $(this).data('jobid');
    $('#confirm-delete-modal').data('jobid', job_id).modal('show');
  });
  $('#confirm-delete-btn').click(function() {
    var job_id = $('#confirm-delete-modal').data('jobid');
    $.post("${url("delete_job_object")}", {job_id: job_id}, function(response) {
      $('#confirm-delete-modal').modal('hide');
      if (response.status == 0) {
        window.location.reload();
      }
      else {
        $.jHueNotify.error("Job results not found.");
      }
    }, "json").error(function(){
      $('#confirm-delete-modal').modal('hide');
      $.jHueNotify.error("Job results not found.");
    });
  });

});
</script>
${commonfooter(messages)| n,unicode}
