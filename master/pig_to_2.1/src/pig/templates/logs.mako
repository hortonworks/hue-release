<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Pig", "pig", user, "100px")}
${shared.menubar(section='Logs')}

## Use double hashes for a mako template comment
## Main body
<div class="container-fluid">
  <div class="row-fluid">
    <div class="span9">
    <table>
    <tr>
      <td>id</td>
      <td>script name</td>
      <td>status</td>
      <td>start time</td>
      <td>end time</td>
    </tr>
      % for log in logs:
        <tr>
          <td>${log.id}</td>
          <td>${log.script_name}</td>
          <td>${log.status}</td>
          <td>${log.start_time}</td>
          <td>${log.end_time}</td>
	</tr>
      % endfor
    </table>
    </div>
  </div>
</div>
${commonfooter()}
