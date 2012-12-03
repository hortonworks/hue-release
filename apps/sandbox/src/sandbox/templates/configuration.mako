<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Sandbox", "sandbox", user, "100px")}
${shared.menubar(section='configuration')}

<div class="container-fluid">
	<h1 id="describe-header">Sandbox configuration</h1>
	<div id="update-tutorials-spinner"><h1>Updating tutorials...&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
	<h3 id="update-tutorials-msg"></h3>
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
        <td><div id=${component['name']}>${component['version']}</div></td>
        <td><a href="#" class="btn" id="updateTutorialsBtn">Update</a></td>
      % else:
        <td colspan="2"><div id=${component['name']}>${component['version']}</div></td>
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
    function showError(msg){
        $('#update-tutorials-msg').html(msg);
        $('#update-tutorials-spinner').hide();
        $('#describe-header').show();
        $('#update-tutorials-msg').show();
    }
	$(document).ready(function(){
	    $.ajaxSetup({
            error: function(jqXHR, exception) {
                if (jqXHR.status === 0) {
                    showError("Update tutorials failed: you are offline. Please check your network.");
                } else if (jqXHR.status == 404) {
                    showError("Update tutorials failed: requested page not found.");
                } else if (jqXHR.status == 500) {
                    showError("Update tutorials failed: internal server error.");
                } else if (exception === 'parsererror') {
                    showError("Update tutorials failed: requested JSON parse failed.");
                } else if (exception === 'timeout') {
                    showError("Update tutorials failed: time out error.");
                } else if (exception === 'abort') {
                    showError("Update tutorials failed: ajax request aborted.");
                } else {
                    showError("Update tutorials failed: unknown error.");
                }
            }
        });
	
		$("#updateTutorialsBtn").click(function(){
			$('#describe-header').hide();
       		$('#update-tutorials-spinner').show();
            $.post("${url("sandbox.views.index")}", function(data){
            if (data.on_success_url != "")
            {
                $('#update-tutorials-msg').text("");
                //window.location.href = data.on_success_url
                for (var i=0; i<data.components.length; i++)
                {
                    var cur = $('div#' + data.components[i].name);
                    var curVersion = cur.text();
                    //alert(curVersion + "|" + data.components[i].version );
                    if(curVersion != data.components[i].version)
                    {
                        $('div#' + data.components[i].name).html(data.components[i].version);
                        showError("Tutorials were successfully updated to " + data.components[i].version + " version");
                        window.location.reload(true);
                        return;
                    }
                }
                if(data.error != ""){
                    showError("Update tutorials failed: " + data.error);
                }
                else{
                    showError("There are no available tutorial updates");
                }
                return;
            }
            }, "json");
      });
	});
</script>

${commonfooter()}
