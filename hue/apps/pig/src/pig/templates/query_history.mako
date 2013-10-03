<%!
from desktop.views import commonheader, commonfooter 
from pig.models import Job
%>
<%namespace name="shared" file="shared_components.mako" />

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
      <th>Delete</tr>
    </tr>
</thead>
<tbody>
% for job in jobs.object_list:
    <tr>
      <td>${job.start_time.strftime('%d.%m.%Y %H:%M')}</td>
      <td><a href="${url("show_job_result", job_id=job.job_id)}">${job.script.title}</a></td>
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
      <td><a href="${url("delete_job_object", job_id=job.job_id)}" onClick="return confirm('Are you sure you want to delete job result?');"><i class="icon-trash"></i> Delete</a></td>
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
${commonfooter(messages)| n,unicode}
