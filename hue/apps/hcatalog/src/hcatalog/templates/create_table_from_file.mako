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
${ commonheader(_("HCatalog: Create table manually"), app_name, user, '100px') | n,unicode }
${layout.menubar(section='tables')}

<div class="container-fluid" id="container-fluid-top">
    <h1 id="describe-header">${_('Create a new table from a file')}</h1>
    <div id="action-spinner-create"><h1>${_('Creating the table...')}&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
    <div id="action-spinner-preview"><h1>${_('Processing the file to preview...')}&nbsp;<img src="/static/art/spinner.gif" width="16" height="16"/></h1></div>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    <li>
                        <a href="${ url(app_name + ':import_wizard', database=database)}">${_('Create a new table from a file')}</a>
                    </li>
                    <li>
                        <a href="${ url(app_name + ':create_from_file', database=database)}">${_('Create a new table from a file New')}</a>
                    </li>
                    <li>
                        <a href="${ url(app_name + ':create_table', database=database)}">${_('Create a new table manually')}</a>
                    </li>
                </ul>
            </div>
        </div>

        <div class="span9">
            <div id="alert-error-main" class="alert alert-error">
                <p><strong>The following error(s) occurred:</strong></p>
                <pre id="error-message">The error message</pre>
                <small></small>
            </div>

            <form action="#" method="POST" id="mainForm" class="form-horizontal">
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
                                            <span  class="help-inline error-inline error-inline-bis hide">${_('Table with this name already exists. Table names must be globally unique.')}</span>
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
                                <tr>
                                    <td>
                                        <div class="control-group">
                                            ${comps.bootstrapLabel(table_form["field_terminator"])}
                                            <div class="controls">
                                                ${comps.field(table_form["field_terminator"], render_default=True)}
                                                <span class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed. Terminator must be exactly one character.')}</span>
                                                </span>
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
                                    show_errors=False
                                    )}
                                    ${comps.field(table_form["file_type"], render_default=True)}
                                    <input id="submit-preview" class="btn btn-primary disable-feedback"
                                           value="${_('Preview')}" name="submitPreview"/>
                                    <span class="help-inline error-inline hide">${_('This field is required. Select path to the file on HDFS.')}</span>
                                </div>
                            </div>
                        </div>
                        <div class="well" id="file-options-csv">
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
                                                </span>
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
                                            ${comps.bootstrapLabel(table_form["ignore_whitespaces"])}
                                            <div class="controls">
                                                ${comps.field(table_form["ignore_whitespaces"], render_default=True)}
                                            </div>
                                        </div>
                                    </td>

                                </tr>
                            </table>
                        </div>
                        <div id="preview-div">
                            <div class="alert alert-info">${_('Table preview')}</div>
                            <div class="scrollable"></div>
                        </div>
                    </fieldset>
                </div>
                <div class="form-actions">
                    <input id="submit-create" type="submit" name="createTable" class="btn btn-primary disable-feedback"
                           value="${_('Create table')}"/>
                </div>
                <div id="hidden-form-box">
                    ${comps.field(table_form["formatted_path"], render_default=True)}
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

    #alert-error-main {
        display: none;
    }

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

    div.well#file-options-csv {
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
        text-align: right
    }

    #id_table-file_type {
        width: 120px;
    }

    #submit-preview {
        width: 90px;
    }

    #filechooser {
        min-height: 100px;
        overflow-y: scroll;
        margin-top: 10px;
    }

    .pathChooser {
        width: 50%;
    }

    .error-inline {
        color: #B94A48;
        font-weight: bold;
    }

    div .alert {
        margin-bottom: 5px;
    }

    #action-spinner-create, #action-spinner-preview, #hidden-form-box {
        display: none;
    }

</style>

</div>

<script type="text/javascript" charset="utf-8">

var filePath = "";
function reactOnFilePathChange(newPath) {
    ##    if(filePath !== newPath)
        {
        filePath = newPath;
        var ext = filePath.toLowerCase().split('.').pop();
        if (ext == "csv" || ext == "tsv") {
            $("#id_table-file_type").val("csv");
        }
        else if (ext == "xls" || ext == "xlsx") {
            $("#id_table-file_type").val("xls");
        }
        else {
            $("#id_table-file_type").val("undef");
        }
        $("#id_table-file_type").change();
    }
}

var tableList = [];

$(document).ready(function () {
    $(document).resize()
    var zoom = document.documentElement.clientWidth / window.innerWidth;
    $(window).resize(function () {
        var zoomNew = document.documentElement.clientWidth / window.innerWidth;
        if (zoom != zoomNew) {
            $(".scrollable").css("max-width", $(".form-actions").outerWidth() + "px");
            zoom = zoomNew
        }
    });
    $(".scrollable").css("max-width", $(".form-actions").outerWidth() + "px");

    $('#id_table-autodetect_delimiter').change(function(){
        if($(this).is(":checked")) {
            $("#id_table-delimiter_0").attr("disabled", "disabled");
            $("#id_table-delimiter_1").attr("disabled", "disabled");
         }
        else {
            $("#id_table-delimiter_0").removeAttr("disabled");
            $("#id_table-delimiter_1").removeAttr("disabled");
        }
        $("#id_table-delimiter_0").change();
    });
    $("#id_table-autodetect_delimiter").change();

    $("#id_table-field_terminator_1").addClass("input-small");
    $("#id_table-field_terminator_1").css("margin-left", "4px").attr("placeholder", "${_('type here')}");
    $("#id_table-field_terminator_0").change(function () {
        if ($(this).val() == "__other__") {
            $("#id_table-field_terminator_1").css("visibility", "visible");
        }
        else {
            $("#id_table-field_terminator_1").css("visibility", "hidden");
            $("#id_table-field_terminator_1").val('');
        }
    });
    $("#id_table-field_terminator_0").change();


    $("#id_table-delimiter_1").addClass("input-small");
    $("#id_table-delimiter_1").css("margin-left", "4px").attr("placeholder", "${_('type here')}");
    $("#id_table-delimiter_0").change(function () {
        if ($(this).val() == "__other__") {
            $("#id_table-delimiter_1").css("visibility", "visible");
        }
        else {
            $("#id_table-delimiter_1").css("visibility", "hidden");
            $("#id_table-delimiter_1").val('');
        }
    });
    $("#id_table-delimiter_0").change();

    $("#id_table-file_type").change(function () {
        $("#preview-div").hide();
        if ($(this).val() == "csv") {
            $("div.well#div-file-selector").addClass("div-file-selector");
            $("#file-options-csv").show();
            unlockControls();
        }
        else if ($(this).val() == "xls") {
            $("#file-options-csv").hide();
            $("div.well#div-file-selector").removeClass("div-file-selector");
            lockControls();
        }
        else if ($(this).val() == "msaccess") {
            $("#file-options-csv").hide();
            $("div.well#div-file-selector").removeClass("div-file-selector");
            lockControls();
        }
    });
    $("#id_table-file_type").val("csv");
    $("#id_table-file_type").change();

% if error is not None:
    showMainError("${error}");
% endif

    $.post("${url(app_name + ':get_tables')}",function (data) {
        tableList = data;
    }, "json");

    $("#submit-preview").click(function () {
        submitPreviewStart();
        $("#preview-div").hide();
        if (!validateForm()) {
            submitPreviewEnd();
            return;
        }
        var postQueryData = $('form#mainForm').serializeArray();
        postQueryData.push({ name: "submitPreviewAction", value: "" });
        $.post("${url(app_name + ':create_from_file', database=database)}", postQueryData,function (data) {
            if ("error" in data) {
                showMainError(data["error"]);
            }
            else if ("results" in data) {
                $('.scrollable').html(data["results"]);
                $("#preview-div").show();
                $('html, body').animate({
                    scrollTop: $("#preview-div").offset().top - $("#container-fluid-top").offset().top
                }, 1000);
            }
            if ("options" in data) {
                updateOptions(data["options"]);
            }
            submitPreviewEnd();
        }, "json").error(function () {
                    submitPreviewEnd();
                });
    });

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


    $("#submit-create").click(function (event) {
        if (!validateOnCreateTable()) {
            event.preventDefault();
        }
        else {
            submitCreateStart();
        }
    });

    function updateOption(optionName, options)
    {
        if(optionName in options ) {
            $("#id_table-" + optionName).val(options[optionName])
        }
    }

    function updateOptions(options)
    {
        updateOption("field_terminator_0", options);
        updateOption("field_terminator_1", options);
        updateOption("delimiter_0", options);
        updateOption("delimiter_1", options);
        updateOption("formatted_path", options);
    }

    function submitPreviewStart() {
        hideMainError();
        lockControls();
        $('#action-spinner-preview').show();
        $('#describe-header').hide();
        $(window).scrollTop(0);
    }

    function submitPreviewEnd() {
        $('#action-spinner-preview').hide();
        $('#describe-header').show();
        unlockControls();
    }

    function submitCreateStart() {
        hideMainError();
        lockControls();
        $('#action-spinner-create').show();
        $('#describe-header').hide();
        $(window).scrollTop(0);
    }

    function submitCreateEnd() {
        $('#action-spinner-create').hide();
        $('#describe-header').show();
        unlockControls();
    }

    function lockControls() {
        $("#submit-preview").attr("disabled", "disabled");
        $("#submit-create").attr("disabled", "disabled");
    }

    function unlockControls() {
        $("#submit-preview").removeAttr("disabled");
        $("#submit-create").removeAttr("disabled");
    }

    function validateOnCreateTable() {
        var scrollTo = 0;
        var isValid = true;
        isValid = validateForm();
        $(".column").each(function () {
            var _field = $(this);
            if (!isDataValid($.trim(_field.val()))) {
                showFieldError(_field);
                if (scrollTo == 0) {
                    scrollTo = $(this).position().top - $(this).closest(".well").height();
                }
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

        var filePath = $("input[name='table-path']");
        if (!isDataValid($.trim(filePath.val()))) {
            showFieldError(filePath);
            isValid = false;
        }
        else {
            hideFieldError(filePath);
        }

        var fieldTerminatorFld = $("#id_table-field_terminator_1");
        if ($("#id_table-field_terminator_0").val() == "__other__" && (!isDataValid($.trim(fieldTerminatorFld.val())) || $.trim(fieldTerminatorFld.val()).length != 1)) {
            showFieldError(fieldTerminatorFld);
            isValid = false;
        }
        else {
            hideFieldError(fieldTerminatorFld);
        }

        var delimiterFld = $("#id_table-delimiter_1");
        if ($("#id_table-delimiter_0").val() == "__other__" && (!isDataValid($.trim(delimiterFld.val())) || $.trim(delimiterFld.val()).length != 1)) {
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

    function showMainError(errorMessage) {
        $("#error-message").text(errorMessage);
        $("#alert-error-main").show();
        $(window).scrollTop(0);
    }

    function hideMainError(errorMessage) {
        $("#alert-error-main").hide();
    }

    function showFieldError(field) {
        field.nextAll(".error-inline").not(".error-inline-bis").removeClass("hide");
    }

    function hideFieldError(field) {
        if (!(field.nextAll(".error-inline").hasClass("hide"))) {
            field.nextAll(".error-inline").addClass("hide");
        }
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
