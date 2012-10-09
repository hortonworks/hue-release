## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.

<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Pig", "pig", "100px")}
${shared.menubar(section='My Scripts')}

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
        <p>
    <a href="${url('pig.views.delete', v.id)}">
    <img src="/pig/static/art/delete.gif" alt="Delete" height="12" width="12">
    </a>
    <a href="${url('pig.views.script_clone', v.id)}">
	<img src="/pig/static/art/clone.png" alt="Delete" height="14" width="14">
	</a>
	<a href="${url('pig.views.one_script', v.id)}">
	    % if v.title: 
	         ${v.title}
            % else:
                 no title
            % endif
    </a>
        </p>
      </li>
      % endfor
	</ul>
    <a class="btn" href="${url('new_script')}">New script</a>
      </div>
    </div>
    <div class="span9" style="float: left; width: 70%;">
      <div class="clearfix">
	<div class="div_conteiner">
      % if text:
      <pre>${text}</pre>
      % endif
    </div>
        <div class="input">
	  <form action="${url('pig.views.new_script')}" method="post">
        ${form}
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
