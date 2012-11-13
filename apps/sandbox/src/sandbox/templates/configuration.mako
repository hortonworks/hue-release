<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Sandbox", "sandbox", user, "100px")}
${shared.menubar(section='configuration')}

<div class="container-fluid">
	<h1 id="describe-header">Sandbox configuration</h1>
<div class="span-5">
<table class="table table-bordered">
<thead>
    <tr>
      <th>Component</th>
      <th colspan="2">Version</th>
    </tr>
</thead>
<tbody>
% for component in components:
    <tr>
      <td>${component['name']}</td>
      % if 'updateButton' in component:
        <td>${component['version']}</td>
        <td><a href="#" class="btn">Update</a></td>
      % else:
        <td colspan="2">${component['version']}</td>
      % endif
    </tr>
% endfor
</tbody>
</table>
</div>
</div>
${commonfooter()}
