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
${commonheader("HCatalog: Create Table", "hcatalog", "100px")}
${layout.menubar(section='create table')}
<div class="container-fluid">
<h1> How Do You Want to Create Your Table? </h1>
<div class="row-fluid">
  <div class="span3">
  	<div class="well sidebar-nav">
    	<ul class="nav nav-list">
    		<li class="nav-header">Actions</li>
       		<li class="clearfix"><a href="${ url('hcatalog.create_table.import_wizard')}">Create From File</a></li>
       		<li class="clearfix"><a href="${ url('hcatalog.create_table.create_table')}">Create Manually</a></li>
    	</ul>
    </div>
  </div>
</div>
</div>
${commonfooter()}
