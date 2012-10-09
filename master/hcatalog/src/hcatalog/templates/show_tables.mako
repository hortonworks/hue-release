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
${commonheader("HCatalog: Table List", "hcatalog", "100px")}
${layout.menubar(section='tables')}

<div class="container-fluid">
	<h1>HCatalog: Table List</h1>
	<div class="row-fluid">
		<div class="span3">
			<div class="well sidebar-nav">
				<ul class="nav nav-list">
					<li class="nav-header">Actions</li>
		      		<li><a href="${ url('hcatalog.create_table.import_wizard')}">Create a new table from file</a></li>
					<li><a href="${ url('hcatalog.create_table.create_table')}">Create a new table manually</a></li>
				</ul>
			</div>
		</div>
		<div class="span9">
			${debug_info}
			<table class="table table-condensed table-striped datatables">
				<thead>
					<tr>
						<th>Table Name</th>
						<th>&nbsp;</th>
					</tr>
				</thead>
				<tbody>
				% for table in tables:
					<tr>
						##<td><a href="${ url("hcatalog.views.describe_table", table=table) }" data-row-selector="true">${ table }</a></td>
						##<td><a href="${ url("hcatalog.views.read_table", table=table) }" class="btn">Browse Data</a></td>
						<td><a href="#" data-row-selector="true">${ table }</a></td>
						<td><a href="#" class="btn">Browse Data</a></td>
					</tr>				
				% endfor
				</tbody>
			</table>
		</div>
	</div>
</div>


<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
			"bInfo": false,
			"bFilter": false,
			"aoColumns": [
				null,
				{ "sWidth": "130px", "bSortable" : false },
			 ]
		});

		$("a[data-row-selector='true']").jHueRowSelector();
	});
</script>

${commonfooter()}
