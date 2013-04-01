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
from django.utils.translation import ugettext as _
%>
<%namespace name="layout" file="layout.mako" />
${ commonheader(_('HCatalog: Table List'), app_name, user, '100px') | n,unicode }
${layout.menubar(section='tables')}

<div class="container-fluid">
	<h1 id="describe-header">${_('HCatalog: Table List')}</h1>
	<div id="action-spinner"><h1>${_('Loading a table list...')}&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
	<div class="row-fluid">
		<div class="span3">
			<div class="well sidebar-nav">
				<ul class="nav nav-list">
					<li class="nav-header">${_('Actions')}</li>
					<li><a href="${ url(app_name + ':create_from_file', database=database)}">${_('Create a new table from a file')}</a></li>
					<li><a href="${ url(app_name + ':create_table', database=database)}">${_('Create a new table manually')}</a></li>
				</ul>
			</div>
		</div>
		<div class="span9">
			<table class="table table-condensed table-striped datatables" id="table-list-tbl">
				<thead>
					<tr>
						<th>${_('Table Name')}</th>
						<th>&nbsp;</th>
					</tr>
				</thead>
				<tbody id=table-body>
				</tbody>
			</table>
		</div>
	</div>
</div>

<style>
	#table-list-tbl, #action-spinner {
		display:none;
	}
</style>

<script type="text/javascript" charset="utf-8">
	function showError(msg) {
		//alert(msg);
	}
	
	function onBrowse()
	{
		$(".btn.btn-primary.browse").attr("disabled", "disabled");
		$(".btn.btn-primary.browse").addClass("disabled");
	}
	
	$(document).ready(function(){
		var dataTbl = $(".datatables").dataTable({
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
		
		$('#describe-header').hide();
		$('#action-spinner').show();
		$.post("${url(app_name + ':get_tables')}", function(data){
			for (var i = 0; i < data.length; i++){
			    dataTbl.fnAddData([
			    "<a href=" + "/hcatalog/table/" + "${database}" + "/" + data[i] + ">" + data[i] + "</a>",
			    "<a href=" + "/hcatalog/table/" + "${database}" + "/" + data[i] + "/read" + " class=\"btn btn-primary browse\" onclick=\"onBrowse()\">${_('Browse Data')}</a>"
			    ]);
			}

			$('#action-spinner').hide();
			$('#describe-header').show();
			$('#table-list-tbl').show();
			return;
		}, "json").error(function() {
			$('#action-spinner').hide();
			$('#describe-header').show();
			$('table-list-tbl').show();
		});
	});
</script>

${ commonfooter(messages) | n,unicode }
