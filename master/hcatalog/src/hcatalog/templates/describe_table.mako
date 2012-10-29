## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
## http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.
<%!
from desktop.views import commonheader, commonfooter
%>
<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="hcatalog_components.mako" />
<%
##  if is_view:
##    view_or_table_noun = "View"
##  else:
    view_or_table_noun = "Table"
%>

<%
  if len(table['partitions']) > 0:
    has_partitions = True
  else:
    has_partitions = False
%>

${commonheader("HCatalog %s Metadata: %s" % (view_or_table_noun, table['tableName']), "hcatalog", user, "100px")}
${layout.menubar(section='tables')}
<%def name="column_table(cols)">

    <table class="table table-striped table-condensed datatables">
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Comment</th>
        </tr>
      </thead>
      <tbody>
        % for column in cols:
          <tr>
            <td>${ column['name'] }</td>
            <td>${ column['type'] }</td>
            % if 'comment' in column:
            	<td>${ column['comment'] }</td>
            % else:
            	<td>${ "" }</td>
            % endif
          </tr>
        % endfor
      </tbody>
    </table>

</%def>

<div class="container-fluid">
	<h1 id="describe-header">HCatalog Table Metadata: ${table['tableName']}</h1>
	<div id="browse-spinner"><h1>Getting partition location...&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
	<div class="row-fluid">
		<div class="span3">
			<div class="well sidebar-nav">
				<ul class="nav nav-list">
					<li class="nav-header">Actions</li>
					<li><a href="#importData" data-toggle="modal">Import Data</a></li>
					<li><a href="${ url("hcatalog.views.read_table", table=table_name) }">Browse Data</a></li>
			        <li><a href="#dropTable" data-toggle="modal">Drop ${view_or_table_noun}</a></li>
					<br>
					<li><a href="${url('hcatalog.views.hive_view', table=table_name)}">View in Hive</a></li>
					<li><a href="${url('hcatalog.views.pig_view', table=table_name)}">View in Pig</a></li>

				</ul>
			</div>
		</div>
		<div class="span9">
			<ul class="nav nav-tabs">
				<li class="active"><a href="#columns" data-toggle="tab">Columns</a></li>
		        % if len(table['partitionKeys']) > 0:
					<li><a href="#partitionColumns" data-toggle="tab">Partition Columns</a></li>
		        % endif
		        % if is_table_partitioned:
			        <li><a href="#partitions" data-toggle="tab">Partitions</a></li>
			    % endif
			</ul>

			<div class="tab-content">
				<div class="active tab-pane" id="columns">
					${column_table(table['columns'])}
				</div>
		        % if len(table['partitionKeys']) > 0:
		          <div class="tab-pane" id="partitionColumns">
		            ${column_table(table['partitionKeys'])}
		          </div>
		        % endif
		        ## start of partitions
		        <div class="tab-pane" id="partitions">
		        <table class="table table-striped table-condensed partitiontable">
		          <thead>
		            <tr>
                      <th>Partitions</th>
                    </tr>
				  </thead>
				  <tbody>
                  % if is_table_partitioned and has_partitions:
                    % for indx, partition in enumerate(table['partitions']):
                      <tr>
                        <td><a href="#" data-row-selector="true">${partition['name']}</a></td>
                        <td><a href="#" class="btn browsePartitionLocation" partitionname=${partition['name']}>Browse</a></td>
                        <td><a href="#dropPartition${indx}" data-toggle="modal" class="btn">Drop</a></td>
                    </tr>
                    % endfor
                  % else:
                    <tr><td>Table has no partitions.</td></tr>
                  % endif
                    </tbody>
				  </table>
                </div>
		        ## end of partitions
			</div>
		</div>
	</div>
</div>


<div id="dropTable" class="modal hide fade">
	<form id="dropTableForm" method="POST" action="${ url("hcatalog.views.drop_table", table=table_name) }">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>Drop Table</h3>
	</div>
	<div class="modal-body">
	  <div class="dropTableMessage">

	  </div>
	</div>
	<div class="modal-footer">
		<input type="submit" class="btn primary" value="Yes"/>
		<a href="#" class="btn secondary hideModal">No</a>
	</div>
	</form>
</div>


% if is_table_partitioned and has_partitions:
  % for indx, part in enumerate(table['partitions']):
<div id="dropPartition${indx}" class="modal hide fade">
	<form id="dropPartitionForm" method="POST" action="${ url("hcatalog.views.drop_partition", table=table_name) }">
	<input id="partition_name" type="hidden" value=${part['name']} name="partition_name"/>
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>Drop Partition</h3>
	</div>
	<div class="modal-body">
	  <div class="alert dropPartitionMessage">
	  </div>
	</div>
	<div class="modal-footer">
		<input type="submit" class="btn primary submitDropPartition" value="Yes"/>
		<a href="#" class="btn secondary hideModal">No</a>
	</div>
	</form>
</div>
  % endfor
% endif

<div id="importData" class="modal hide fade">
	<form method="POST" action="${ url("hcatalog.views.load_table", table=table_name) }" class="form-stacked">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>Import data</h3>
	</div>
	<div class="modal-body">
	  <div class="alert">
	        <p>Note that loading data will move data from its location into the table's storage location.</p>
	  </div>


	  <div class="clearfix">
	  ${comps.label(load_form["path"], title_klass='loadPath', attrs=dict(
        ))}
    	<div class="input">
		     ${comps.field(load_form["path"], title_klass='loadPath', attrs=dict(
		       klass='loadPath input-xlarge'
		       ))}
		</div>
		</div>

      % for pf in load_form.partition_columns:
		<div class="clearfix">
			${comps.label(load_form[pf], render_default=True)}
	    	<div class="input">
	        	${comps.field(load_form[pf], render_default=True, attrs=dict(
			       klass='input-xlarge'
			       ))}
			</div>
		</div>

      % endfor

		<div class="clearfix">
			<div class="input">
				<input type="checkbox" name="overwrite"/> Overwrite existing data
			</div>
		</div>


	<div id="filechooser">
	</div>
	</div>

	<div class="modal-footer">
		<input type="submit" class="btn primary" value="Submit"/>
		<a href="#" class="btn secondary" data-dismiss="modal">Cancel</a>
	</div>
	</form>
</div>
</div>

   
<style>
	#filechooser {
		display:none;
		min-height:100px;
		overflow-y:scroll;
		margin-top:10px;
	}
	#browse-spinner {
		display:none;
	}
</style>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
	
		$('.browsePartitionLocation').click(function() {
			$('#describe-header').hide();
       		$('#browse-spinner').show();
			return false;
		});

		$("#filechooser").jHueFileChooser({
			onFileChoose: function(filePath){
				$(".loadPath").val(filePath);
				$("#filechooser").slideUp();
			},
			createFolder: false
		});
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
			"bInfo": false,
			"bFilter": false
		});

		$.getJSON("${ url("hcatalog.views.drop_table", table=table_name) }",function(data){
			$(".dropTableMessage").text(data.title);
		});
		$(".hideModal").click(function(){
			$(this).closest(".modal").modal("hide");
		});
		$(".loadPath").click(function(){
			$("#filechooser").slideDown();
		});
		
		
		$(".partitiontable").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
			"bInfo": false,
			"bFilter": false,
			"bAutoWidth": false,
			"aoColumns": [
				{ "sWidth": "80%", "bSortable" : false },
             % if has_partitions:
				{ "sWidth": "10%", "bSortable" : false },
				{ "sWidth": "10%", "bSortable" : false },
             % endif
			 ]
		});

		$("a[data-row-selector='true']").jHueRowSelector();
		
		$.getJSON("${ url("hcatalog.views.drop_partition", table=table_name) }",function(data){
			$(".dropPartitionMessage").text(data.title);
		});
		
		$(".browsePartitionLocation").click(function(){
            $.post("${url("hcatalog.views.browse_partition", table=table_name)}", {partition_name:$(this).attr('partitionname')}, function(data){
            if (data.url != "")
            {
                window.location.href = data.url;
                return;
            } 
            }, "json");
      });

	});
</script>

${commonfooter()}
