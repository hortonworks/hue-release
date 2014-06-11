## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="util" file="util.mako" />

${ commonheader(_('Create table from file'), app_name, user, '100px') | n,unicode }
${layout.menubar(section='tables')}

<div class="container-fluid">
    <h1>${_('Create a new table from a file')}</h1>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    <li><a href="${ url(app_name + ':import_wizard', database=database)}">${_('Create a new table from a file')}</a></li>
                    <li><a href="${ url(app_name + ':create_table', database=database)}">${_('Create a new table manually')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
            <ul class="nav nav-pills">
                <li><a id="step1" href="#">${_('Step 1: Choose File')}</a></li>
                <li class="active"><a href="#">${_('Step 2: Choose Delimiter')}</a></li>
                <li><a id="step3" href="#">${_('Step 3: Define Columns')}</a></li>
            </ul>
            <form id="delimiterForm" action="${action}" method="POST" class="form-horizontal"> ${ csrf_token_field | n } 
                <div class="hide">
                    ${util.render_form(file_form)}
                    ${comps.field(delim_form['file_type'])}
                </div>
                <fieldset>
                    <div class="alert alert-info"><h3>${_('Choose a Delimiter')}</h3>
                        % if initial:
                            ${_('Beeswax has determined that this file is delimited by')} <strong>${delim_readable}</strong>.
                        % endif
                    </div>
                    <div class="control-group">
                        ${comps.bootstrapLabel(delim_form["delimiter"])}
                        <div class="controls">
                            ${comps.field(delim_form["delimiter"], render_default=True)}
                            <input id="submit_preview" class="btn btn-info" type="submit" value="${_('Preview')}" name="submit_preview"/>
                            <span class="help-block">
                            ${_('Enter the column delimiter. Must be a single character. Use syntax like "\\001" or "\\t" for special characters.')}
                            </span>
                        </div>
                    </div>
                    <div class="control-group">
                        ${comps.bootstrapLabel(delim_form["read_column_headers"])}
                        <div class="controls">
                            ${comps.field(delim_form["read_column_headers"], render_default=True)}
                            <span class="help-block">
                        ${_('Check this box if you want to read first row of the file as columns header.')}
                            </span>
                        </div>
                    </div>
                    <div class="control-group">
                        <label class="control-label">${_('Table preview')}</label>
                        <div class="controls">
                            <div class="scrollable">
                                <table class="table table-striped table-condensed">
                                    <thead>
                                    <tr/>
                                    <tr id="preview-header-1">
                                            % for i in range(n_cols):
                                                <th>col_${i+1}</th>
                                            % endfor
                                    </tr>
                                    <tr id="preview-header-2">
                                            % if fields_list:
                                                % for val in fields_list[0]:
                                                    <th>${val}</th>
                                                % endfor
                                            % endif
                                    </tr>
                                    </thead>
                                    <tbody>
                                            % if fields_list:
                                                <tr id="first-data-row">
                                                    % for val in fields_list[0]:
                                                        <td>${val}</td>
                                                    % endfor
                                                </tr>
                                                % for row in fields_list[1:]:
                                                <tr>
                                                    % for val in row:
                                                        <td>${val}</td>
                                                    % endfor
                                                </tr>
                                                % endfor
                                            % endif
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </fieldset>

                <div class="form-actions">
                    <input class="btn" type="submit" value="${_('Previous')}" name="cancel_delim"/>
                    <input class="btn btn-primary" type="submit" name="submit_delim" value="${_('Next')}" />
                </div>
            </form>
        </div>
    </div>
</div>

<style>
    .scrollable {
        width: 100%;
        overflow-x: auto;
    }
</style>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $(".scrollable").width($(".form-actions").width());

        $("#id_read_column_headers").change(function(){
            if ($(this).is(":checked")){
                $("#preview-header-1").hide();
                $("#first-data-row").hide();
                $("#preview-header-2").show();
            }
            else {
                $("#preview-header-2").hide();
                $("#preview-header-1").show();
                $("#first-data-row").show();
            }
        });
        $("#id_read_column_headers").change();

        $("#id_delimiter_1").css("margin-left","4px").attr("placeholder","${_('Please type your delimiter here')}").hide();
        $("#id_delimiter_0").change(function(){
            if ($(this).val() == "__other__"){
                $("#id_delimiter_1").show();
            }
            else {
                $("#id_delimiter_1").hide();
                $("#id_delimiter_1").val('');
            }
        });

        $("#id_delimiter_0").change();

        $("#step1").click(function(e){
            e.preventDefault();
            $("input[name='cancel_delim']").click();
        });
        $("#step3").click(function(e){
            e.preventDefault();
            $("input[name='submit_delim']").click();
        });
        $("body").keypress(function(e){
            if(e.which == 13){
                e.preventDefault();
                $("input[name='submit_delim']").click();
            }
        });
    });
</script>

${ commonfooter(messages) | n,unicode }
