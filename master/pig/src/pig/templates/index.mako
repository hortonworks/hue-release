<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Pig", "pig", "100px")}
${shared.menubar(section='mytab')}

## Use double hashes for a mako template comment
## Main body
<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3" style="float: left; width: 20%;">
      <div class="well sidebar-nav">
	<h2>My scripts</h2>
	<ul class="nav nav-list">
      % for v in pig_script:
      <li>
	<a href="${url('pig.views.one_script', v.id)}">
	    % if v.title: 
	         ${v.title}
            % else:
                 no title
            % endif
        </a>
      </li>
      % endfor
	</ul>
      </div>
    </div>
    <div class="span9" style="float: left; width: 70%;">
      <div class="clearfix">
        <div class="input">
	  <form action="${url('pig.views.index')}" method="post">
	    <table>
	      <tr>
		<td>
		  <input id="id_title" type="text" name="title" maxlength="100" />
		</td>
	      </tr>
	      <tr>
		<td>
		  <textarea id="id_text" rows="10" cols="40" name="text"></textarea>
		</td>
	      </tr>
	    </table>
	    <div class="actions">
	      <input class="btn primary" type="submit" name="submit" value="Save" >
	    </div>
	  </form>
	</div>
      </div>
    </div>
  </div>
</div>
    <script type="text/javascript" >
      var editor = CodeMirror.fromTextArea(document.getElementById("id_text"), {
        lineNumbers: true,
        matchBrackets: true,
        indentUnit: 4,
        mode: "text/x-pig"
      });
    </script>
${commonfooter()}
