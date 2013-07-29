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
<%
    default_header_msg = _('HCatalog: Database List')
%>
${ commonheader(default_header_msg, app_name, user, '100px') | n,unicode }
${layout.menubar(section='databases')}

<div class="container-fluid">
    <div><h1 id="header-msg">${default_header_msg}</h1></div>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    <li>
                        <a href="${ url(app_name + ':create_database')}">${_('Create a new database')}</a>
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
                            <button id="dropBtn" class="btn toolbarBtn" title="${_('Delete the selected databases')}"
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

<div id="dropDatabase" class="modal hide fade">
    <form id="dropDatabaseForm" method="POST"> ${ csrf_token_field | n }
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>

            <h3 id="dropDatabaseMessage">${_('Confirm action')}</h3>
        </div>
        <div class="modal-footer">
            <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}"/>
            <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
        </div>
        <div class="hide">
            <select name="database_selection" data-bind="options: availableDatabases, selectedOptions: chosenDatabases"
                    size="5" multiple="true"></select>
        </div>
    </form>
</div>

<script src="/hcatalog/static/js/hcatalog_scripts.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">

    function setHeaderMsg(msg, hasSpinner) {
        if (hasSpinner) {
            $("#header-msg").html(msg + '&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/>')
        }
        else {
            $("#header-msg").html(msg);
        }
    }

    function gettingDatabases(flag) {
        if (flag) {
            setHeaderMsg("${_('Loading the database list...')}", true);
        }
        else {
            setHeaderMsg("${default_header_msg}", false);
        }
    }

    function droppingDatabases(flag) {
        if (flag) {
            setHeaderMsg("${_('Dropping the database(s)...')}", true);
        }
        else {
            setHeaderMsg("${default_header_msg}", false);
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

        var viewModel = {
            availableDatabases: ko.observableArray([]),
            chosenDatabases: ko.observableArray([])
        };
        ko.applyBindings(viewModel);
        var databases = undefined;

        $(document).on("change paste keyup", "#filterInput", function () {
            if (databases != undefined) {
                databases.fnFilter($(this).val());
            }
        });

        $("#id_database").change(function () {
            $.cookie("hueHcatalogLastDatabase", $(this).val(), {expires:90, path:"/"});
            getDatabases($(this).val());
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

        $(document).on("click", ".databaseCheck", function () {
            if ($(this).attr("checked")) {
                $(this).removeClass("icon-ok").removeAttr("checked");
            }
            else {
                $(this).addClass("icon-ok").attr("checked", "checked");
            }
            $(".selectAll").removeAttr("checked").removeClass("icon-ok");
            toggleActions();
        });

        $(document).on("click", "td a", function () {
            $.cookie("hueHcatalogLastDatabase", $(this).text(), {expires:90, path:"/"});
        });

        function toggleActions() {
            $(".toolbarBtn").attr("disabled", "disabled");
            var selector = $(".hueCheckbox[checked='checked']").not(".selectAll");
            if (selector.length >= 1) {
                $("#dropBtn").removeAttr("disabled");
            }
        }

        $(document).on("click", "#dropBtn", function () {
            viewModel.chosenDatabases.removeAll();
            $(".hueCheckbox[checked='checked']").each(function (index) {
                viewModel.chosenDatabases.push($(this).data("drop-name"));
            });
            $("#dropDatabase").modal("show");
        });

        $('form#dropDatabaseForm').submit(function (event) {
            event.preventDefault();
            $(this).closest(".modal").modal("hide");
            droppingDatabases(true);
            $.post("${url(app_name + ':drop_database')}", $(this).serializeArray(),function (data) {
                if ("error" in data) {
                    showMainError(decodeUnicodeCharacters(data["error"]));
                }
                else if ("on_success_url" in data && data.on_success_url)
                {
                    window.location.replace(data.on_success_url);
                    return;
                }
                droppingDatabases(false);
            }, "json").error(function () {
                        droppingDatabases(false);
                    });

        });

        $.getJSON("${ url(app_name + ':drop_database')}", function (data) {
            $("#dropDatabaseMessage").text(data.title);
        });

        getDatabases();
        function getDatabases() {
            gettingDatabases(true);
            $.post("${url(app_name + ':show_databases')}",function (data) {
                if ("error" in data) {
                    showMainError(decodeUnicodeCharacters(data["error"]));
                }
                else if ("database_list_rendered" in data && "databases" in data) {
                    $('#table-wrap').html(data["database_list_rendered"]);
                    viewModel.availableDatabases = data["databases"];
                    databases = $(".datatables").dataTable({
                        "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
                        "bPaginate": false,
                        "bLengthChange": false,
                        "bInfo": false,
                        "bFilter": true,
                        "aoColumns": [
                            {"bSortable": false, "sWidth": "1%" },
                            null
                        ],
                        "oLanguage": {
                            "sEmptyTable": "${_('No databases available')}",
                            "sZeroRecords": "${_('No matching records')}"
                        }
                    });
                    $("a[data-row-selector='true']").jHueRowSelector();
                    gettingDatabases(false);
                }
            }, "json").error(function () {
                        gettingDatabases(false);
                    });
        }

    });
</script>

${ commonfooter(messages) | n,unicode }
