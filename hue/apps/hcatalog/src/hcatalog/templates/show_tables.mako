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
<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />
${ commonheader(_('HCatalog: Table List'), app_name, user, '100px') | n,unicode }
${layout.menubar(section='tables')}

<div class="container-fluid">
    <h1 id="main-spin">${_('HCatalog: Table List')}</h1>

    <div id="getting-tables-spin" class="hidden-initially" data-bind="visible: gettingTables">
        <h1>${_('Loading the table list...')}&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1>
    </div>
    <div id="dropping-tables-spin" class="hidden-initially" data-bind="visible: droppingTables">
        <h1>${_('Dropping the table(s)...')}&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <span>
                        <li class="nav-header">${_('database')}</li>
                        <li>
                            <form action="${ url(app_name + ':show_tables') }" id="db_form"
                                    method="POST"> ${ csrf_token_field | n }
                                    ${ db_form | n,unicode }
                            </form>
                        </li>
                    </span>

                    <li class="nav-header">${_('Actions')}</li>
                    <li>
                        <a href="${ url(app_name + ':create_from_file')}">${_('Create a new table from a file')}</a>
                    </li>
                    <li>
                        <a href="${ url(app_name + ':create_table')}">${_('Create a new table manually')}</a>
                    </li>
                </ul>
            </div>
        </div>
        <div class="span9">
            <div id="alert-error-main" class="alert alert-error hidden-initially">
                <p><strong>The following error(s) occurred:</strong></p>
                <pre id="error-message"/>
                <small></small>
            </div>
            <div>
                <%actionbar:render>
                    <%def name="actions()">
                            <button id="dropBtn" class="btn toolbarBtn" title="${_('Delete the selected tables')}"
                                    disabled="disabled"><i class="icon-trash"></i>  ${_('Drop')}</button>
                    </%def>
                </%actionbar:render>
                <div id="table-wrap"/>
            </div>
        </div>
    </div>
</div>

<style>
    .hidden-initially {
        display: none;
    }
</style>

<div id="dropTable" class="modal hide fade">
    <form id="dropTableForm" method="POST"> ${ csrf_token_field | n }
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>

            <h3 id="dropTableMessage">${_('Confirm action')}</h3>
        </div>
        <div class="modal-footer">
            <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}"/>
            <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
        </div>
        <div class="hide">
            <select name="table_selection" data-bind="options: availableTables, selectedOptions: chosenTables" size="5"
                    multiple="true"></select>
        </div>
    </form>
</div>

<script src="/hcatalog/static/js/hcatalog_scripts.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">

    function onBrowse() {
        $(".btn.btn-primary.browse").attr("disabled", "disabled");
        $(".btn.btn-primary.browse").addClass("disabled");
    }

    function gettingTables(flag) {
        if (flag) {
            $("#main-spin").hide();
            $("#getting-tables-spin").show();
        }
        else {
            $("#getting-tables-spin").hide();
            $("#main-spin").show();

        }
    }

    function droppingTables(flag) {
        if (flag) {
            $("#main-spin").hide();
            $("#dropping-tables-spin").show();
        }
        else {
            $("#dropping-tables-spin").hide();
            $("#main-spin").show();
        }
    }

    function showMainError(errorMessage) {
        $("#error-message").text(errorMessage);
        $("#alert-error-main").show();
        $(window).scrollTop(0);
    }

    function hideMainError() {
        $("#alert-error-main").hide();
    }

    $(document).ready(function () {
        init();
        var viewModel = {
            availableTables: ko.observableArray([]),
            chosenTables: ko.observableArray([])
        };
        ko.applyBindings(viewModel);
        var tables = undefined;

        $(document).on("change paste keyup", "#filterInput", function () {
            if (tables != undefined) {
                tables.fnFilter($(this).val());
            }
        });

        $("#id_database").change(function () {
            $.cookie("hueHcatalogLastDatabase", $(this).val(), {expires: 90, path: "/"});
            getTables();
        });

        $(document).on("click", ".selectAll", function () {
            if ($(this).attr("checked")) {
                $(this).removeAttr("checked").removeClass("icon-ok");
                $("." + $(this).data("selectables")).removeClass("icon-ok").removeAttr("checked");
            }
            else {
                $(this).attr("checked", "checked").addClass("icon-ok");
                $("." + $(this).data("selectables")).addClass("icon-ok").attr("checked", "checked");
            }
            toggleActions();
        });

        $(document).on("click", ".tableCheck", function () {
            if ($(this).attr("checked")) {
                $(this).removeClass("icon-ok").removeAttr("checked");
            }
            else {
                $(this).addClass("icon-ok").attr("checked", "checked");
            }
            $(".selectAll").removeAttr("checked").removeClass("icon-ok");
            toggleActions();
        });

        function init() {
            $.cookie("hueHcatalogLastDatabase", "${database}", {expires: 90, path: "/"});
            getTables();
        }

        function toggleActions() {
            $(".toolbarBtn").attr("disabled", "disabled");
            var selector = $(".hueCheckbox[checked='checked']").not(".selectAll");
            if (selector.length >= 1) {
                $("#dropBtn").removeAttr("disabled");
            }
        }

        $(document).on("click", "#dropBtn", function () {
            viewModel.chosenTables.removeAll();
            $(".hueCheckbox[checked='checked']").each(function (index) {
                viewModel.chosenTables.push($(this).data("drop-name"));
            });
            $("#dropTable").modal("show");
        });

        $('form#dropTableForm').submit(function (event) {
            event.preventDefault();
            $(this).closest(".modal").modal("hide");
            droppingTables(true);
            var postData = $(this).serializeArray();
            postData.push({ name: "database", value: $("#id_database").val() });
            $.post("${url(app_name + ':drop_table')}", postData,function (data) {
                if ("error" in data) {
                    showMainError(decodeUnicodeCharacters(data["error"]));
                }
                else if ("on_success_url" in data && data.on_success_url) {
                    window.location.replace(data.on_success_url);
                    return;
                }
                droppingTables(false);
            }, "json").error(function () {
                        droppingTables(false);
                    });

        });
        $.getJSON("${ url(app_name + ':drop_table')}",
                { name: "database", value: $("#id_database").val() }, function (data) {
                    $("#dropTableMessage").text(data.title);
                });

        function getTables() {
            gettingTables(true);
            $.post("${url(app_name + ':show_tables')}",function (data) {
                if ("error" in data) {
                    showMainError(decodeUnicodeCharacters(data["error"]));
                }
                else if ("table_list_rendered" in data && "tables" in data) {
                    $('#table-wrap').html(data["table_list_rendered"]);
                    viewModel.availableTables = data["tables"];
                    tables = $(".datatables").dataTable({
                        "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
                        "bPaginate": false,
                        "bLengthChange": false,
                        "bInfo": false,
                        "bFilter": true,
                        "aoColumns": [
                            {"bSortable": false, "sWidth": "1%" },
                            null,
                            {"bSortable": false, "sWidth": "130px" }
                        ],
                        "oLanguage": {
                            "sEmptyTable": "${_('No tables available')}",
                            "sZeroRecords": "${_('No matching records')}"
                        }
                    });
                    $("a[data-row-selector='true']").jHueRowSelector();
                    gettingTables(false);
                }
            }, "json").error(function () {
                        gettingTables(false);
                    });
        }

    });
</script>

${ commonfooter(messages) | n,unicode }
