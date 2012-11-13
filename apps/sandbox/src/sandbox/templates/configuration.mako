<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Sandbox", "sandbox", user, "100px")}
${shared.menubar(section='configuration')}

<div class="container-fluid">
	<h1 id="describe-header">Sandbox configuration</h1>
	<div id="update-tutorials-spinner"><h1>Updating tutorials...&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
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
        <td><a href="#" class="btn" id="updateTutorialsBtn">Update</a></td>
      % else:
        <td colspan="2">${component['version']}</td>
      % endif
    </tr>
% endfor
</tbody>
</table>
</div>
</div>

<style>
	#update-tutorials-spinner {
		display:none;
	}
</style>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$("#updateTutorialsBtn").click(function(){
			$('#describe-header').hide();
       		$('#update-tutorials-spinner').show();
            $.post("${url("sandbox.views.index")}", function(data){
            if (data.on_success_url != "")
            {
                window.location.href = data.on_success_url;
                return;
            } 
            }, "json");
      });
	});
</script>

${commonfooter()}
