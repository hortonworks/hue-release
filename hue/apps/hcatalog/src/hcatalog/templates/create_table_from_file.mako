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

<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />
${ commonheader(_("HCatalog: Create a new table from a file"), app_name, user, '100px') | n,unicode }
${layout.menubar(section='tables')}

<div class="container-fluid" id="container-fluid-top">
<h1 id="main-spin">${_('Create a new table from a file')}</h1>

<div id="creating-table-spin" class="hidden-initially"><h1>${_('Creating the table...')}&nbsp;<img
        src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
<div id="importing-data-spin" class="hidden-initially"><h1>${_('Importing data into the table...')}&nbsp;<img
        src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
<div id="preview-data-spin" class="hidden-initially" data-bind="visible: previewData()">
    <h1>${_('Processing the file to preview...')}&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1>
</div>
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
<form action="#" method="POST" id="mainForm" class="form-horizontal"> ${ csrf_token_field | n }
<div>
    <fieldset>
        <div class="alert alert-info">${_('Table options')}</div>
        <div class="well">
            <table>
                </tr>
                <td>
                    <div class="control-group">
                        ${comps.bootstrapLabel(table_form["name"])}
                        <div class="controls">
                            ${comps.field(table_form["name"], attrs=dict(placeholder=_('table_name'), ))}
                            <span class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                            <span class="help-inline error-inline error-inline-bis hide">${_('Table with this name already exists. Table names must be globally unique.')}</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="control-group">
                        ${comps.bootstrapLabel(table_form["comment"])}
                        <div class="controls">
                            ${comps.field(table_form["comment"], attrs=dict(placeholder=_('Optional'),))}
                        </div>
                    </div>
                </td>
                </tr>
            </table>
        </div>
        <div class="alert alert-info">${_('File options')}</div>
        <div class="well" id="div-file-selector">
            <div class="control-group">
                ${comps.bootstrapLabel(table_form["path"])}
                <div class="controls">
                    ${comps.field(table_form["path"],
                    placeholder="/user/user_name/data_dir",
                    klass="pathChooser",
                    file_chooser=True,
                    show_errors=False,
                    attrs={'autocomplete':'off'}
                    )}
                    <span class="help-inline error-inline hide">${_('This field is required. Select path to the file on HDFS.')}</span>
                </div>
                <input id="file-type" name="file_type" value="text" style="display: none"/>
            </div>
        </div>
        <div class="well" id="file-options-text">
            <table>
                </tr>
                <td>
                    <div class="control-group">
                        ${comps.bootstrapLabel(table_form["encoding"])}
                        <div class="controls">
                            ${comps.field(table_form["encoding"], render_default=True)}
                        </div>
                    </div>
                </td>
                <td>
                    <div class="control-group">
                        ${comps.bootstrapLabel(table_form["read_column_headers"])}
                        <div class="controls">
                            ${comps.field(table_form["read_column_headers"], render_default=True)}
                        </div>
                    </div>
                </td>
                <td>
                    <div class="control-group">
                        ${comps.bootstrapLabel(table_form["import_data"])}
                        <div class="controls">
                            ${comps.field(table_form["import_data"], render_default=True)}
                        </div>
                    </div>
                </td>
                </tr>
                <tr>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["delimiter"])}
                            <div class="controls">
                                ${comps.field(table_form["delimiter"], render_default=True)}
                                <span class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed. Terminator must be exactly one character.')}</span>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["autodetect_delimiter"])}
                            <div class="controls">
                                ${comps.field(table_form["autodetect_delimiter"], render_default=True)}
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["ignore_whitespaces"])}
                            <div class="controls">
                                ${comps.field(table_form["ignore_whitespaces"], render_default=True)}
                            </div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["replace_delimiter_with"])}
                            <div class="controls">
                                ${comps.field(table_form["replace_delimiter_with"], render_default=True)}
                                <span class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed. Terminator must be exactly one character.')}</span>
                                </span>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["java_style_comments"])}
                            <div class="controls">
                                ${comps.field(table_form["java_style_comments"], render_default=True)}
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["ignore_tabs"])}
                            <div class="controls">
                                ${comps.field(table_form["ignore_tabs"], render_default=True)}
                            </div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["single_line_comment"])}
                            <div class="controls">
                                ${comps.field(table_form["single_line_comment"], render_default=True)}
                            </div>
                        </div>
                    </td>
                    <td></td>
                    <td></td>
                </tr>
            </table>
        </div>
        <div class="well" id="file-options-ss">
            <table>
                <tr>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["xls_sheet"])}
                            <div class="controls">
                                ${comps.field(table_form["xls_sheet"], render_default=True)}
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["xls_cell_range"])}
                            <div class="controls">
                                ${comps.field(table_form["xls_cell_range"], attrs=dict(placeholder=_('e.g. A1:D30'),))}
                                <span class="help-inline error-inline hide">${_('Cell range must be in excel format (e.g. A1:D30). You could leave this parameter empty to match all cells.')}</span>
                            </div>
                        </div>
                    </td>
                    <td>
                    </td>
                </tr>
                <tr>
                    <td>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["xls_read_column_headers"])}
                            <div class="controls">
                                ${comps.field(table_form["xls_read_column_headers"], render_default=True)}
                            </div>
                        </div>
                    </td>
                    <td></td>
                    <td></td>
                </tr>
            </table>
        </div>

        <div id="preview-div">
            <div class="alert alert-info">${_('Table preview')}</div>
            <div class="scrollable"></div>
            <div class="pagination pull-right" id="preview-pagination">
                <ul>
                    <li id="submit-preview-begin" class="prev"><a title="${_('Beginning of List')}"
                                                                  href="javascript:void(0)">&larr; ${_('Beginning of List')}</a>
                    </li>
                    <li id="submit-preview-next"><a title="${_('Next page')}"
                                                    href="javascript:void(0)">${_('Next Page')} &rarr;</a>
                    </li>
                </ul>
            </div>
        </div>
    </fieldset>
</div>
<input name="file_processor_type" data-bind="value: fileProcessorType" value="" style="display: none"/>

<div class="form-actions">
    <input id="submit-create" type="submit" name="createTable" class="btn btn-primary disable-feedback"
           value="${_('Create table')}"/>
</div>
</form>
</div>
</div>
</div>


<div id="chooseFile" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>

        <h3>${_('Choose a file')}</h3>
    </div>
    <div class="modal-body">
        <div id="filechooser">
        </div>
    </div>
    <div class="modal-footer">
    </div>
</div>


<style>
    div.well.div-file-selector {
        margin-bottom: 0px;
        box-shadow: 0 0 0;
        border-bottom-width: 0px;
        -webkit-border-bottom-left-radius: 0px;
        -webkit-border-bottom-right-radius: 0px;
        -moz-border-radius-bottomleft: 0px;
        -moz-border-radius-bottomright: 0px;
    }

    div.well.div-file-selector-only {

    }

    div.well#file-options-text {
        padding-top: 0px;
        border-top-width: 0px;
        box-shadow: 0 0 0;
        -webkit-border-top-left-radius: 0px;
        -webkit-border-top-right-radius: 0px;
        -moz-border-radius-topleft: 0px;
        -moz-border-radius-topright: 0px;
    }

    div.well#file-options-ss {
        padding-top: 0px;
        border-top-width: 0px;
        box-shadow: 0 0 0;
        -webkit-border-top-left-radius: 0px;
        -webkit-border-top-right-radius: 0px;
        -moz-border-radius-topleft: 0px;
        -moz-border-radius-topright: 0px;
    }

    .scrollable {
        overflow-x: auto;
        margin-top: 10px;
    }

    .control-label {
        float: left;
        width: 100px;
        padding-top: 5px;
        text-align: right;
    }

    #filechooser {
        min-height: 100px;
        overflow-y: scroll;
        margin-top: 10px;
    }

    .pathChooser {
        width: 80%;
    }

    .error-inline {
        color: #B94A48;
        font-weight: bold;
    }

    div .alert {
        margin-bottom: 5px;
    }

    .hidden-initially {
        display: none;
    }

    .resultTable td, .resultTable th {
        white-space: nowrap;
    }

    #div-file-selector .controls {
        width: 80%;
    }

    .notFound {
        background-color: #f09999 !important;
    }
</style>

</div>

<script src="/hcatalog/static/js/hcatalog_scripts.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">

var PreviewType = {"preview": 0, "preview_next": 1, "preview_beginning": 2};
var FileType = {"text": "text", "spreadsheet": "spreadsheet", "none": "none"};

var tableList = [];
var previewStartIdx = 0;
var previewEndIdx = 0;
var filePath = "";
var fileType = FileType.none
var pingHiveJobTimer = null;
var replaceDelimiterWithAuto = true;
var viewModel = new AppViewModel();

function AppViewModel() {
    var self = this;
    self.fileProcessorType = ko.observable("");
}
ko.applyBindings(viewModel);

function importingData(flag) {
    lockControls(flag);
    if (flag) {
        $("#main-spin").hide();
        $("#importing-data-spin").show();
    }
    else {
        $("#importing-data-spin").hide();
        $("#main-spin").show();
    }
}

function creatingTable(flag) {
    lockControls(flag);
    if (flag) {
        $("#main-spin").hide();
        $("#creating-table-spin").show();
    }
    else {
        $("#creating-table-spin").hide();
        $("#main-spin").show();
    }
}

function previewData(flag) {
    lockControls(flag);
    if (flag) {
        $("#main-spin").hide();
        $("#preview-data-spin").show();
    }
    else {
        $("#preview-data-spin").hide();
        $("#main-spin").show();
    }
}

function lockControls(flag) {
    if (flag) {
        $("#submit-preview-begin").prop('disabled', true);
        $("#submit-preview-next").prop('disabled', true);
        $("#submit-create").prop('disabled', true);
    }
    else {
        $("#submit-preview-begin").prop('disabled', false);
        $("#submit-preview-next").prop('disabled', false);
        $("#submit-create").prop('disabled', false);
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

    initUI();
    function submitPreview(preview_type) {
        submitPreviewStart();
        if (PreviewType.preview == preview_type) {
            $("#preview-div").hide();
        }
        if (!validatePreviewForm()) {
            submitPreviewEnd();
            return;
        }
        var postQueryData = $('form#mainForm').serializeArray();
        postQueryData.push({ name: "file_type", value: fileType });
        if (PreviewType.preview == preview_type) {
            postQueryData.push({ name: "submitPreviewAction", value: "" });
        }
        else if (PreviewType.preview_next == preview_type) {
            postQueryData.push({ name: "submitPreviewNext", value: "" });
            postQueryData.push({ name: "preview_start_idx", value: previewStartIdx });
            postQueryData.push({ name: "preview_end_idx", value: previewEndIdx });
        }
        else if (PreviewType.preview_beginning == preview_type) {
            postQueryData.push({ name: "submitPreviewBeginning", value: "" });
            postQueryData.push({ name: "preview_start_idx", value: previewStartIdx });
            postQueryData.push({ name: "preview_end_idx", value: previewEndIdx });
        }
        $.post("${url(app_name + ':create_from_file', database=database)}", postQueryData,function (data) {
            if ("error" in data) {
                showMainError(decodeUnicodeCharacters(data["error"]));
            }
            if ("results" in data) {
                $('.scrollable').html(data["results"]);
                $(".resultTable").dataTable({
                    "bPaginate": false,
                    "bLengthChange": false,
                    "bInfo": false,
                    "bFilter": false,
                    "bSort": false,
                    "oLanguage": {
                        "sEmptyTable": "${_('No data available')}",
                        "sZeroRecords": "${_('No matching records')}"
                    },
                    "fnDrawCallback": function (oSettings) {
                        $(".resultTable").jHueTableExtender({
                            hintElement: "#jumpToColumnAlert",
                            firstColumnTooltip: true
                        });
                    }
                });
                $("#preview-div").show();
            }
            if ("options" in data) {
                updateOptions(data["options"]);
                if ("preview_start_idx" in data["options"]) {
                    previewStartIdx = data["options"]["preview_start_idx"];
                }
                if ("preview_end_idx" in data["options"]) {
                    previewEndIdx = data["options"]["preview_end_idx"];
                }
                if ("preview_has_more" in data["options"]) {
                    if (data["options"]["preview_has_more"]) {
                        $("#submit-preview-next").show();
                    }
                    else {
                        $("#submit-preview-next").hide();
                    }
                }
                if ("file_processor_type" in data["options"]) {
                    viewModel.fileProcessorType(data["options"]["file_processor_type"]);
                }
            }
            submitPreviewEnd();
        }, "json").error(function () {
                    submitPreviewEnd();
                });
    };

    $("#submit-preview").click(function () {
        submitPreview(PreviewType.preview)
    });
    $("#submit-preview-next").click(function () {
        submitPreview(PreviewType.preview_next)
    });
    $("#submit-preview-begin").click(function () {
        submitPreview(PreviewType.preview_beginning)
    });

    $(".fileChooserBtn").addClass("btn-primary disable-feedback");
    $(".fileChooserBtn").text("Choose a file");
    $(".fileChooserBtn").click(function (e) {
        e.preventDefault();
        var _destination = $(this).attr("data-filechooser-destination");
        $("#filechooser").jHueFileChooser({
            initialPath: $("input[name='" + _destination + "']").val(),
            onFileChoose: function (filePath) {
                reactOnFilePathChange(filePath);
                $("input[name='" + _destination + "']").val(filePath);
                $("#chooseFile").modal("hide");
            },
            createFolder: false
        });
        $("#chooseFile").modal("show");
    });

    var pathChooser = $('.pathChooser');

    pathChooser.typeahead({
        source: function (path,resp) {
            pathChooser.removeClass('notFound');
            if (path.slice(-1) != '/') path = path.replace(/\\/g,'/').replace(/\/[^\/]*$/, '')+'/';
            $.get(
                "/filebrowser/view" + path,
                function (data) {
                    var complitions = [];
                    if (data.error != null) {
                      $.jHueNotify.error(data.error);
                      pathChooser.addClass('notFound');
                      complitions.length = 0;
                    } else {
                      $(data.files).each(function (cnt, item) {
                        itm_name = item.name;
                        if (itm_name != ".") {
                          var _ico = "icon-file";
                          if (item.type == "dir") {
                            _ico = "icon-folder-close";
                          }
                          complitions.push(path+itm_name);
                        }
                      });
                      window.setTimeout(function () {
                        return resp(complitions);
                      }, 50);  // timeout for IE8
                    }
                },'json'
            );
        },
        updater: function (item) {
            $.get("/filebrowser/view" + item,
                function (data) {
                    if (data.type=='file') {
                        reactOnFilePathChange(pathChooser.val())}
                },'json');
            return item;
        },
        items:15
    });

    $('form#mainForm').submit(function (event) {
        if (!validateOnCreateTable()) {
            event.preventDefault();
        }
        else {
            submitCreateStart();
        }
    });

    $("#id_database").change(function () {
        $.cookie("hueHcatalogLastDatabase", $(this).val(), {expires: 90, path: "/"});
    });

    function setFileType(ft) {
        fileType = ft;
        $("input[name='file_type']").val(ft);
    }

    function initUI() {
        setFileType(FileType.none);
        $("#file-options-text").hide();
        $("#file-options-ss").hide();
        $("#preview-div").hide();
        $("div.well#div-file-selector").removeClass("div-file-selector");

        $(document).resize();
        var zoom = document.documentElement.clientWidth / window.innerWidth;
        $(window).resize(function () {
            var zoomNew = document.documentElement.clientWidth / window.innerWidth;
            if (zoom != zoomNew) {
                $(".scrollable").css("max-width", $(".form-actions").outerWidth() + "px");
                zoom = zoomNew;
            }
        });
        $(".scrollable").css("max-width", $(".form-actions").outerWidth() + "px");

        % if error is not None:
                showMainError("${error}");
        % endif

        $.post("${url(app_name + ':list_tables_json')}", function (data) {
            tableList = data;
        }, "json");
    }

    % if job_id and on_success_url:
            creatingTable(false);
            importingData(true);
            pingHiveJob("${job_id}", "${on_success_url}");
    % endif

    function reactOnFilePathChange(newPath) {
        filePath = newPath;
        $(".pathChooser").val(filePath);
        if (filePath.indexOf(".csv") != -1 || filePath.indexOf(".tsv") != -1 ||
                filePath.indexOf(".dsv") != -1 || filePath.indexOf(".txt") != -1) {
            setFileType(FileType.text);
            $("div.well#div-file-selector").addClass("div-file-selector");
            $("#file-options-ss").hide();
            $("#preview-pagination").hide();
            $("#file-options-text").show();
        }
        else if (filePath.indexOf(".xls") != -1 || filePath.indexOf(".xlsx") != -1) {
            setFileType(FileType.spreadsheet);
            $("#file-options-text").hide();
            $("#preview-pagination").show();
            $("#file-options-ss").show();
            $("div.well#div-file-selector").addClass("div-file-selector");
        }
        else {
            setFileType(FileType.text);
            $("div.well#div-file-selector").addClass("div-file-selector");
            $("#file-options-ss").hide();
            $("#preview-pagination").hide();
            $("#file-options-text").show();
        }
        reactOnOptionChange();
    }

    function reactOnOptionChange() {
        submitPreview(PreviewType.preview);
    }

    // text files
    $("select[name='table-encoding']").change(reactOnOptionChange);
    $("input[name='table-read_column_headers']").change(reactOnOptionChange);
    var delim0 = $("select[name='table-delimiter_0']");
    var delim1 = $("input[name='table-delimiter_1']");
    delim1.addClass("input-small");
    delim1.css("margin-left", "4px").attr("placeholder", "${_('type here')}");
    delim1.css("visibility", "hidden");
    delim1.val('');
    delim0.change(function () {
        if (delim0.val() == "__other__") {
            delim1.css("visibility", "visible");
        }
        else {
            delim1.css("visibility", "hidden");
            delim1.val('');
        }
        $("input[name='table-autodetect_delimiter']").prop('checked', false);
        reactOnOptionChange();
    });
    delim1.bind("change paste keyup", reactOnOptionChange);
    terminatorFieldInit("replace_delimiter_with");
    $("input[name='table-ignore_whitespaces']").change(reactOnOptionChange);
    $("input[name='table-ignore_tabs']").change(reactOnOptionChange);
    $("input[name='table-java_style_comments']").change(reactOnOptionChange);
    $("input[name='table-single_line_comment']").bind("change paste keyup", reactOnOptionChange);
    $("input[name='table-autodetect_delimiter']").change(function () {
        if ($(this).is(":checked")) {
            replaceDelimiterWithAuto = true;
            reactOnOptionChange();
        }
    });

    // spreadsheet files
    $("select[name='table-xls_sheet']").change(reactOnOptionChange);
    $("input[name='table-xls_cell_range']").bind("change paste keyup", reactOnOptionChange);
    $("input[name='table-xls_read_column_headers']").change(reactOnOptionChange);

    function terminatorFieldInit(name) {
        var field_0 = $("#id_table-" + name + "_0");
        var field_1 = $("#id_table-" + name + "_1");
        field_1.addClass("input-small");
        field_1.css("margin-left", "4px").attr("placeholder", "${_('type here')}");
        field_0.change(function () {
            reactOnOptionChange();
            if ($(this).val() == "__other__") {
                field_1.css("visibility", "visible");
            }
            else {
                field_1.css("visibility", "hidden");
                field_1.val('');
            }
        });
        field_1.bind("change paste keyup", reactOnOptionChange);
    }

    function updateTerminatorField(name) {
        var delim0 = $("#id_table-" + name + "_0");
        var delim1 = $("#id_table-" + name + "_1");
        if (replaceDelimiterWithAuto) {
            replaceDelimiterWithAuto = false;
            var delim_repl_with0 = $("select[name='table-replace_delimiter_with_0']");
            var delim_repl_with1 = $("input[name='table-replace_delimiter_with_1']");
            delim_repl_with0.val(delim0.val());
            delim_repl_with1.val(delim1.val());
            if (delim_repl_with0.val() == "__other__") {
                delim_repl_with1.css("visibility", "visible");
            }
            else {
                delim_repl_with1.css("visibility", "hidden");
                delim_repl_with1.val('');
            }
        }
        if (delim0.val() == "__other__") {
            delim1.css("visibility", "visible");
        }
        else {
            delim1.css("visibility", "hidden");
            delim1.val('');
        }
    }

    function updateOption(optionName, options) {
        if (optionName in options) {
            $("#id_table-" + optionName).val(options[optionName]);
        }
    }

    function updateListOption(optionName, listOptionName, options) {
        if (optionName in options && listOptionName in options) {
            var sel = $("#id_table-" + optionName);
            sel.empty(options[optionName]);
            for (var i = 0; i < options[listOptionName].length; i++) {
                sel.append('<option value="' + options[listOptionName][i][0] + '">' + options[listOptionName][i][1] + '</option>');
            }
        }
    }

    function updateOptions(options) {
        updateOption("replace_delimiter_with_0", options);
        updateOption("replace_delimiter_with_1", options);
        updateOption("delimiter_0", options);
        updateOption("delimiter_1", options);
        updateTerminatorField("delimiter");
        updateListOption("xls_sheet", "xls_sheet_list", options);
        updateOption("xls_sheet", options);
    }

    function submitPreviewStart() {
        hideMainError();
        previewData(true);
    }

    function submitPreviewEnd() {
        previewData(false);
    }

    function submitCreateStart() {
        hideMainError();
        creatingTable(true);
        $(window).scrollTop(0);
    }

    function submitCreateEnd() {
        creatingTable(false);
    }

    function validateOnCreateTable() {
        var scrollTo = 0;
        var isValid = true;
        isValid = validateForm();
        $(".column").each(function () {
            var _field = $(this);
            if (!isDataValid($.trim(_field.val()))) {
                showFieldError(_field);
                showMainError("One or more of defined column names are not valid. Make sure that there are no empty column names" +
                        " and each of them is unique. Spaces are not allowed.")
                isValid = false;
            }
            else {
                hideFieldError(_field);
            }
            var _lastSecondErrorField = null;
            $(".column").not("[name='" + _field.attr("name") + "']").each(function () {
                if ($.trim($(this).val()) != "" && $.trim($(this).val()) == $.trim(_field.val())) {
                    _lastSecondErrorField = $(this);
                    if (scrollTo == 0) {
                        scrollTo = _field.position().top - _field.closest(".well").height();
                    }
                    isValid = false;
                }
            });
            if (_lastSecondErrorField != null) {
                showSecondFieldError(_lastSecondErrorField);
            }
            else {
                hideSecondFieldError(_field);
            }
        });
        if (!isValid && scrollTo > 0) {
            $(window).scrollTop(scrollTo);
        }
        return isValid;
    }

    function validateForm() {
        var isValid = true;
        var tableNameFld = $("input[name='table-name']");
        var tableName = $.trim(tableNameFld.val());
        if (!isDataValid(tableName)) {
            showFieldError(tableNameFld);
            isValid = false;
        }
        else {
            hideFieldError(tableNameFld);
        }
        if (tableList.indexOf(tableName) !== -1) {
            showSecondFieldError(tableNameFld);
            isValid = false;
        }
        else {
            hideSecondFieldError(tableNameFld);
        }

        if (!validatePreviewForm()) {
            isValid = false;
        }
        return isValid;
    }

    function validatePreviewForm() {
        var isValid = true;

        var filePathField = $("input[name='table-path']");
        if (!isDataValid(filePath.replace(/ /g,''))) {
            showFieldError(filePathField);
            isValid = false;
        }
        else {
            hideFieldError(filePathField);
        }

        if (fileType == FileType.spreadsheet) {
            var cellRange = $("input[name='table-xls_cell_range']");
            if (cellRange.val().length > 0 && cellRange.attr("placeholder") !== cellRange.val()
                    && cellRange.val().match(/^[a-zA-Z]+\d+:[a-zA-Z]+\d+$/) == undefined) {
                showFieldError(cellRange);
                isValid = false;
            }
            else {
                hideFieldError(cellRange);
            }
        }

        var fieldTerminatorFld = $("#id_table-replace_delimiter_with_1");
        if ($("#id_table-replace_delimiter_with_0").val() == "__other__" &&
                (!isDataValid(fieldTerminatorFld.val() || (fieldTerminatorFld.val().length > 1 && !fieldTerminatorFld.val()[0] != "\\")))) {
            showFieldError(fieldTerminatorFld);
            isValid = false;
        }
        else {
            hideFieldError(fieldTerminatorFld);
        }

        var delimiterFld = $("#id_table-delimiter_1");
        if ($("#id_table-delimiter_0").val() == "__other__" &&
                (!isDataValid(delimiterFld.val() || (delimiterFld.val().length > 1 && !delimiterFld.val()[0] != "\\")))) {
            showFieldError(delimiterFld);
            isValid = false;
        }
        else {
            hideFieldError(delimiterFld);
        }

        return isValid;
    }

    function isDataValid(str) {
        // validates against empty string and no spaces
        return (str != "" && str.indexOf(" ") == -1);
    }

    function showFieldError(field) {
        field.nextAll(".error-inline").not(".error-inline-bis").removeClass("hide");
    }

    function hideFieldError(field) {
        field.nextAll(".error-inline").each(function () {
            if (!($(this).hasClass("hide"))) {
                $(this).addClass("hide");
            }
        });
    }

    function showSecondFieldError(field) {
        field.nextAll(".error-inline-bis").removeClass("hide");
    }

    function hideSecondFieldError(field) {
        if (!(field.nextAll(".error-inline-bis").hasClass("hide"))) {
            field.nextAll(".error-inline-bis").addClass("hide");
        }
    }
});
</script>

${ commonfooter(messages) | n,unicode }
