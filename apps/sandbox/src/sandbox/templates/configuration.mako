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
	$(document).ready(function(){
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
                        $('#update-tutorials-msg').html("Tutorials were successfully updated to " + data.components[i].version + " version");
                        $('#update-tutorials-spinner').hide();
                        $('#describe-header').show();
                        $('#update-tutorials-msg').show();
                        window.location.reload(true);
                        return;
                    }
                }
                $('#update-tutorials-msg').html("There are no available tutorial updates");
                $('#update-tutorials-spinner').hide();
                $('#describe-header').show();
                $('#update-tutorials-msg').show();
                return;
            }

            }, "json").error(function(){
       		    $('#update-tutorials-spinner').hide();
       		    $('#update-tutorials-msg').replaceWith("Update tutorials failed");
                $('#describe-header').show();
                return;
          });
      });
	});
</script>

${commonfooter()}
