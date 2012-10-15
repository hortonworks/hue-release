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

${commonheader("Pig", "pig", user, "100px")}
${shared.menubar(section='PiggyBank')}

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
    <a href="${url('delete', v.id)}">
    <img src="/pig/static/art/delete.gif" alt="Delete" height="12" width="12">
    </a>
    <a href="${url('clone', v.id)}">
	<img src="/pig/static/art/clone.png" alt="Delete" height="14" width="14">
	</a>
	<a href="${url('one_script', v.id)}">
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
      <div class="well sidebar-nav">
      <h2>User-defined Functions</h2>
      <ul class="nav nav-list">
        % for udf in udfs:
        <li><p>
        <a href="${url('udf_del', udf.id)}"><img src="/pig/static/art/delete.gif" alt="Delete" height="12" width="12"></a>
        ${udf.file_name}
        </p></li>
        % endfor
      	<a class="btn" id="displayText" href="#">Add new</a>
        
        <div id="toggleText" style="display: none">
          <form id="udfs" enctype="multipart/form-data" action="${url('piggybank_new')}" method="post">
    	  ${udf_form}
      	  <input class="btn" type="submit" name="submit" value="Add" />
	      </form>
        </div>
	</div>
      </ul>
      </div>
      </div>
    </div>
  </div>
</div>
    <script type="text/javascript" >
       $("#displayText").click(function() {
          var ele = document.getElementById("toggleText");
          var text = document.getElementById("displayText");
          if(ele.style.display == "block") {
              ele.style.display = "none";
          }
          else {
              ele.style.display = "block";
          }
      });
    </script>
${commonfooter()}
