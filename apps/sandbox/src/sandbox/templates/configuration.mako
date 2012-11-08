<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Sandbox", "sandbox", user, "100px")}
${shared.menubar(section='configuration')}

<div class="span-5">
<table class="table table-bordered">
<thead>
    <tr>
      <th>Component</th>
      <th>Version</th>
    </tr>
</thead>
<tbody>
% for component in components:
    <tr>
      <td>${component['name']}</td>
      <td>${component['version']}</td>
    </tr>
% endfor
</tbody>
</table>
</div>
${commonfooter()}
