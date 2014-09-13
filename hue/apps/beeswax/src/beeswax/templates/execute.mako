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
  from desktop.lib.django_util import extract_field_data
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

<%def name="query()">
    % if error_message:
        <div class="alert alert-error">
            <p><strong>${_('Your query has the following error(s):')}</strong></p>
            <p class="queryErrorMessage">${error_message}</p>
            % if log:
                <small>${_('click the')} <b>${_('Error Log')}</b> ${_('tab below for details')}</small>
            % endif
        </div>
    % endif

    <textarea class="span9" rows="35" name="${form.query["query"].html_name}" id="queryField">${extract_field_data(form.query["query"]) or ''}</textarea>

    <div id="validationResults">
    % if len(form.query["query"].errors):
        ${ unicode(form.query["query"].errors) | n,unicode }
     % endif
    </div>
    <br>
    <div class="actions">
        <a id="executeQuery" class="btn btn-primary" tabindex="0">${_('Execute')}</a>
        % if design and not design.is_auto and design.name:
        <a id="saveQuery" class="btn">${_('Save')}</a>
        % endif
        <a id="saveQueryAs" class="btn">${_('Save as...')}</a>
        <a id="explainQuery" class="btn">${_('Explain')}</a>
        &nbsp; ${_('or create a')} &nbsp;<a class="btn" href="${ url(app_name + ':execute_query') }">${_('New query')}</a>
    </div>
</%def>


${ commonheader(_('Query'), 'beeswax', user, '100px') | n,unicode }
${layout.menubar(section='query')}

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <form id="advancedSettingsForm" action="${action}" method="POST" class="form form-horizontal noPadding"> ${ csrf_token_field | n } 
                    <ul class="nav nav-list">
                        <li class="nav-header">${_('database')}</li>
                        <li>
                          ${ form.query['database'] | n,unicode }
                        </li>
                        <li class="nav-header">${_('settings')}</li>
                        <li>
                            % for i, f in enumerate(form.settings.forms):
                            <div class="param">
                                <div class="remove">
                                    ${comps.field(f['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
                                        type="submit",
                                        title=_("Delete this setting"),
                                        klass="btn btn-mini settingsDelete"
                                    ), value=True)}
                                </div>

                                <div class="control-group">
                                    ${comps.label(f['key'])}
                                    ${comps.field(f['key'], attrs=dict(placeholder="mapred.reduce.tasks",
                                        klass="settingsField span8"
                                    ))}
                                </div>

                                <div class="control-group">
                                    ${comps.label(f['value'])}
                                    ${comps.field(f['value'], attrs=dict(
                                        placeholder="1",
                                        klass="span8"
                                    ))}
                                </div>
                            </div>
                            ${comps.field(f['_exists'], hidden=True)}

                            % endfor
                            <div class="control-group">
                                <a class="btn btn-small" data-form-prefix="settings">${_('Add')}</a>
                            </div>
                        </li>
                        <li class="nav-header">
                            ${_('File Resources')}
                        </li>
                        <li>
                            % for i, f in enumerate(form.file_resources.forms):
                            <div class="param">
                                <div class="remove">
                                    ${comps.field(f['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
                                        type="submit",
                                        title=_("Delete this setting"),
                                        klass="btn btn-mini file_resourcesDelete"
                                    ), value=True)}
                                </div>

                                <div class="control-group">
                                    ${comps.label(f['type'])}
                                    ${comps.field(f['type'], render_default=True)}
                                </div>

                                <div class="control-group">
                                    ${comps.label(f['path'])}
                                    ${comps.field(f['path'], attrs=dict(
                                        placeholder="/user/foo/udf.jar",
                                        klass="input-small file_resourcesField span8",
                                        data_filters=f['path'].html_name
                                    ))}
                                </div>
                            </div>
                            ${comps.field(f['_exists'], hidden=True)}

                            % endfor
                            <div class="control-group">
                                <a class="btn btn-small" data-form-prefix="file_resources">${_('Add')}</a>
                            </div>
                        </li>
                        <li class="nav-header">
                            ${_('User-defined Functions')}
                        </li>
                        <li>
                            % for i, f in enumerate(form.functions.forms):
                                <div class="param">
                                    <div class="remove">
                                        ${comps.field(f['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
                                            type="submit",
                                            title=_("Delete this setting"),
                                            klass="btn btn-mini file_resourcesDelete"
                                        ), value=True)}
                                    </div>

                                    <div class="control-group">
                                        ${comps.label(f['name'])}
                                        ${comps.field(f['name'], attrs=dict(
                                            placeholder=_("myFunction"),
                                            klass="span8 functionsField"
                                        ))}
                                    </div>

                                    <div class="control-group">
                                        ${comps.label(f['class_name'])}
                                        ${comps.field(f['class_name'], attrs=dict(
                                            placeholder="com.acme.example",
                                            klass="span8"
                                        ))}
                                    </div>
                                </div>

                              ${comps.field(f['_exists'], hidden=True)}
                            % endfor
                            <div class="control-group">
                                <a class="btn btn-small" data-form-prefix="functions">${_('Add')}</a>
                            </div>
                        </li>
                        <li class="nav-header">${_('Parameterization')}</li>
                        <li>
                            <label class="checkbox" rel="tooltip" data-original-title="${_("If checked (the default), you can include parameters like $parameter_name in your query, and users will be prompted for a value when the query is run.")}">
                                <input type="checkbox" id="id_${form.query["is_parameterized"].html_name | n}" name="${form.query["is_parameterized"].html_name | n}" ${extract_field_data(form.query["is_parameterized"]) and "CHECKED" or ""}/>
                                ${_("Enable Parameterization")}
                            </label>
                        </li>
                          <li class="nav-header">${_('Email Notification')}</li>
                          <li>
                            <label class="checkbox" rel="tooltip" data-original-title="${_("If checked, you will receive an email notification when the query completes.")}">
                                <input type="checkbox" id="id_${form.query["email_notify"].html_name | n}" name="${form.query["email_notify"].html_name | n}" ${extract_field_data(form.query["email_notify"]) and "CHECKED" or ""}/>
                                ${_("Email me on completion")}
                            </label>
                          </li>
                          % if show_execution_engine:
                          <li class="nav-header">${_('Execution engine')}</li>
                          <li>
                            <label class="checkbox" rel="tooltip" data-original-title="${_("If checked, 'hive.execution.engine' will forced set to 'tez'. ")}">
                              <input type="checkbox" id="execute_on_tez">
                              Execute on Tez
                            </label>
                          </li>
                          % endif
                          <li class="nav-header">${_('DIRECT DOWNLOAD')}</li>
                          <li>
                            ${ form.query['download_format'] | n,unicode }
                          </li>
                        </ul>
                    </ul>
                    <input type="hidden" name="${form.query["query"].html_name | n}" class="query" value="" />
                </form>
            </div>

        </div>
        <div class="span9">
            % if on_success_url:
              <input type="hidden" name="on_success_url" value="${on_success_url}"/>
            % endif

            % if design and not design.is_auto and design.name:
              <h1>${_('Query Editor')} : ${design.name}</h1>
              % if design.desc:
                <p>${design.desc}</p>
              % endif
            % else:
              <h1>${_('Query Editor')}</h1>
            % endif 
            <div class="control-group">
                              <a href="javascript:void(0);" class="alert-success" ><i class="icon-question-sign" id="help"></i></a>
                              <div id="help-content" class="hide">
                                <ul class="text-success">
                                  <li>${ _("You can execute queries with multiple SQL statements delimited by a semicolon ';'.") }</li>
                                  <li>Press ctrl+space for autocompletion</li>
                                  <li>To see table fields helper type table_name + "." (e.g. sample_07.)</li>
                                </ul>
                              </div>
            </div>         
            % if error_messages or log:
                <ul class="nav nav-tabs">
                    <li class="active">
                        <a href="#queryPane" data-toggle="tab">${_('Query')}</a>
                    </li>
                    % if error_message or log:
                      <li>
                        <a href="#errorPane" data-toggle="tab">
                        % if log:
                            ${_('Error Log')}
                        % else:
                            &nbsp;
                        % endif
                        </a>
                    </li>
                    % endif
                </ul>

                <div class="tab-content">
                    <div class="active tab-pane" id="queryPane">
                        ${query()}
                    </div>
                    % if error_message or log:
                        <div class="tab-pane" id="errorPane">
                        % if log:
                            <pre>${ log }</pre>
                        % endif
                        </div>
                    % endif
                </div>
            % else:
                ${query()}
            % endif
            <br/>
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

<div id="saveAs" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Choose a name')}</h3>
    </div>
    <div class="modal-body">
      <form class="form-horizontal"> ${ csrf_token_field | n } 
        <div class="control-group">
            <label class="control-label">${_('Name')}</label>
            <div class="controls">
              ${comps.field(form.saveform['name'], klass="input-xlarge")}
              <div class="alert saveAsAlert">
                <i class="icon-warning-sign"></i>
                ${_('This name is already present in Saved Queries.')}</div>
            </div>
        </div>
        <div class="control-group">
            <label class="control-label">${_('Description')}</label>
            <div class="controls">
            ${comps.field(form.saveform['desc'], tag='textarea', klass="input-xlarge")}
            </div>
        </div>
      </form>
    </div>
    <div class="modal-footer">
        <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
        <button id="saveAsNameBtn" class="btn btn-primary">${_('Save')}</button>
    </div>
</div>

<link href="/pig/static/css/codemirror.css" rel="stylesheet">
<link href="/pig/static/css/show-hint.css" rel="stylesheet">

<style>
  h1 {
    margin-bottom: 5px;
  }
  #filechooser {
    min-height: 100px;
    overflow-y: scroll;
  }

  .control-group label {
    float: left;
    padding-top: 5px;
    text-align: left;
    width: 40px;
  }

  .nav-list {
    padding: 0;
  }

  .param {
    background: #FDFDFD;
    padding: 8px 8px 1px 8px;
    border-radius: 4px;
    -webkit-border-radius: 4px;
    -moz-border-radius: 4px;
    margin-bottom: 5px;
    border: 1px solid #EEE;
  }

  .remove {
    float: right;
  }

  .file_resourcesField {
    border-radius: 3px 0 0 3px;
    border-right: 0;
  }

  .fileChooserBtn {
    border-radius: 0 3px 3px 0;
  }

  .saveAsAlert {
    margin: 5px 0px 0px;
    width: 230px;
  }

  /*.linedwrap {
    margin-top: 20px;
    margin-bottom: 10px;
    -webkit-border-radius: 4px;
    -moz-border-radius: 4px;
    border-radius: 4px;
    background-color: #ffffff;
    border: 1px solid #cccccc;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    -moz-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    -webkit-transition: border linear 0.2s, box-shadow linear 0.2s;
    -moz-transition: border linear 0.2s, box-shadow linear 0.2s;
    -o-transition: border linear 0.2s, box-shadow linear 0.2s;
    transition: border linear 0.2s, box-shadow linear 0.2s;
  }*/

  .linedtextarea textarea {
    -webkit-box-shadow: none;
    -moz-box-shadow: none;
    box-shadow: none;
  }

  /*.linedwrap .codelines .lineselect {
    color: #B94A48;
    background-color: #F2DEDE;
  }*/

  .CodeMirror-completions {
    position:absolute;
  }

</style>

<script src="/static/ext/js/jquery/plugins/jquery.cookie.js"></script>
<script src="/pig/static/js/codemirror.js"></script>
<script src="/beeswax/static/js/code-mirror/codemirror-hql.js"></script>
<script src="/beeswax/static/js/code-mirror/codemirror-hql-hint.js"></script>
<script src="/beeswax/static/js/code-mirror/codemirror-show-hint.js"></script>

<script type="text/javascript" charset="utf-8">
    var codeMirror;
    $(document).ready(function(){
        $("*[rel=tooltip]").tooltip({
            placement: 'bottom'
        });
        $("#help").popover({'title': "${'Did you know?'}", 'content': $("#help-content").html(), 'html': true, 'placement': 'bottom'});
        $("a[data-form-prefix]").each(function(){
            var _prefix = $(this).attr("data-form-prefix");
            var _nextID = 0;
            if ($("."+_prefix+"Field").length){
                _nextID= ($("."+_prefix+"Field").last().attr("name").substr(_prefix.length+1).split("-")[0]*1)+1;
            }
            $("<input>").attr("type","hidden").attr("name",_prefix+"-next_form_id").attr("value",_nextID).appendTo($("#advancedSettingsForm"));
            $("."+_prefix+"Delete").click(function(e){
                e.preventDefault();
                $("input[name="+_prefix+"-add]").attr("value","");
                $("<input>").attr("type","hidden").attr("name", $(this).attr("name")).attr("value","True").appendTo($("#advancedSettingsForm"));
                checkAndSubmit();
            });
        });

        $("a[data-form-prefix]").click(function(){
            var _prefix = $(this).attr("data-form-prefix");
            $("<input>").attr("type","hidden").attr("name",_prefix+"-add").attr("value","True").appendTo($("#advancedSettingsForm"));
            checkAndSubmit();
        });

        $(".file_resourcesField").each(function(){
            var self = $(this);
            self.after(getFileBrowseButton(self));
        });

        function getFileBrowseButton(inputElement) {
            return $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function(e){
                e.preventDefault();
                $("#filechooser").jHueFileChooser({
                    initialPath: inputElement.val(),
                    onFileChoose: function(filePath) {
                        inputElement.val(filePath);
                        $("#chooseFile").modal("hide");
                    },
                    createFolder: false
                });
                $("#chooseFile").modal("show");
            })
        }

        $("#id_query-database").change(function(){
             $.cookie("hue${ app_name.capitalize() }LastDatabase", $(this).val(), {path: "/", expires: 90});
        });

        ## If no particular query is loaded
        % if design is None or design.id is None:
            if ($.cookie("hue${ app_name.capitalize() }LastDatabase") != null) {
                $("#id_query-database").val($.cookie("hue${ app_name.capitalize() }LastDatabase"));
            }
        % endif

        var executeQuery = function(){
            $("<input>").attr("type","hidden").attr("name","button-submit").attr("value","Execute").appendTo($("#advancedSettingsForm"));
            % if show_execution_engine:

            var existsId, next_form_id, execute_on_tez = $('#execute_on_tez').is(':checked');

            if (execute_on_tez) {
              if ($('input[name^="settings"][value="hive.execution.engine"]').length > 0) {
                existsId = $('input[name^="settings"][value="hive.execution.engine"]').attr('name').split('-')[1];
                $('input[name="settings-' + existsId + '-value"]').val('tez');
              } else {
                next_form_id = $("#advancedSettingsForm input[name='settings-next_form_id']").val();
                $("#advancedSettingsForm").append(
                  $("<input>").attr("type","hidden").attr("name","settings-" + next_form_id + "-key").attr("value","hive.execution.engine"),
                  $("<input>").attr("type","hidden").attr("name","settings-" + next_form_id + "-value").attr("value","tez"),
                  $("<input>").attr("type","hidden").attr("name","settings-" + next_form_id + "-_exists").attr("value","True")
                );
                $("#advancedSettingsForm input[name='settings-next_form_id']").val(parseInt(next_form_id)+1)
              }
            }
            % endif
            checkAndSubmit();
        }

        $("#executeQuery").click(executeQuery);
        $("#executeQuery").keyup(function(event){
            if(event.keyCode == 13){
                executeQuery();
            }
        });

        $("#saveQuery").click(function(){
            $("<input>").attr("type","hidden").attr("name","saveform-name")
                .attr("value", "${extract_field_data(form.saveform["name"])}").appendTo($("#advancedSettingsForm"));
            $("<input>").attr("type","hidden").attr("name","saveform-desc")
                .attr("value", "${extract_field_data(form.saveform["desc"])}").appendTo($("#advancedSettingsForm"));
            $("<input>").attr("type","hidden").attr("name","saveform-save").attr("value","Save").appendTo($("#advancedSettingsForm"));
            checkAndSubmit();
        });

        var checkSaveAsName = function (field, callback){
            $.post(
                '/beeswax/list_designs',
                {name:field.val()},
                function(data){
                    if (data.thisname) {
                        field.next('.alert').removeClass('hide');
                        $("#saveAsNameBtn").attr("disabled", "disabled");
                    } else {
                        field.next('.alert').addClass('hide');
                        $("#saveAsNameBtn").removeAttr("disabled");
                    }
                    if (typeof callback=='function'){
                        callback(data)
                    }
                },
                'json'
            );
        }

        $("#saveQueryAs").click(function(){
            $("<input>").attr("type","hidden").attr("name","saveform-saveas").attr("value","Save As...").appendTo($("#advancedSettingsForm"));
            $("#saveAs").find("input[name=saveform-name]").keyup(function(){checkSaveAsName($(this));}).trigger('keyup');
            $("#saveAs").modal("show");
        });

        $("#saveAsNameBtn").click(function(){
            checkSaveAsName(
                $("input[name=saveform-name]"),
                function (data){
                    var org_name = $("input[name=saveform-name]").val();
                    var saveasname = (data.thisname) ? org_name + ' (copy)' : org_name;
                    $("<input>").attr("type","hidden").attr("name","saveform-name")
                        .attr("value", saveasname).appendTo($("#advancedSettingsForm"));
                    $("<input>").attr("type","hidden").attr("name","saveform-desc")
                        .attr("value", $("textarea[name=saveform-desc]").val()).appendTo($("#advancedSettingsForm"));
                    checkAndSubmit();
                }
            )
        });

        $("#explainQuery").click(function(){
            $("<input>").attr("type","hidden").attr("name","button-explain").attr("value","Explain").appendTo($("#advancedSettingsForm"));
            checkAndSubmit();
        });

        $("#queryField").change(function(){
            $(".query").val($(this).val());
        });

        $("#queryField").focus(function(){
            $(this).removeClass("fieldError");
            $("#validationResults").empty();
        });

        var selectedLine = -1;
        if ($(".queryErrorMessage")){
          var err = $(".queryErrorMessage").text().toLowerCase();
          var firstPos = err.indexOf("line");
          selectedLine = $.trim(err.substring(err.indexOf(" ", firstPos), err.indexOf(":", firstPos)))*1;
        }

		/*if (selectedLine > -1){
          $("#queryField").linedtextarea({
            selectedLine: selectedLine
          });
        }
        else {
          $("#queryField").linedtextarea();
        }*/

        function checkAndSubmit(){
            if(codeMirror != undefined)
            {
                codeMirror.save();
            }
            $(".query").val($("#queryField").val());
            $("#advancedSettingsForm").submit();
        }

        function autosave(){
          if(codeMirror != undefined)
          {
              codeMirror.save();
          }
          $(".query").val($("#queryField").val());
          $.post("/beeswax/autosave_design/", $("#advancedSettingsForm").serialize());
          return true;
        }

      // =============== CODE-MIRROR ===============
      
      var resizeTimeout = -1;
      var winWidth = $(window).width();
      var winHeight = $(window).height();
      var resizeHeight = function () {
        return $(window).height() - 300 - $('#validationResults').outerHeight() - $("#queryPane .alert-error").outerHeight() - $(".nav-tabs").outerHeight();
      };

      $(window).on("resize", function () {
        window.clearTimeout(resizeTimeout);
        resizeTimeout = window.setTimeout(function () {
          // prevents endless loop in IE8
          if (winWidth != $(window).width() || winHeight != $(window).height()) {
            codeMirror.setSize("95%", resizeHeight());
            winWidth = $(window).width();
            winHeight = $(window).height();
          }
        }, 200);
      });
       
      var currentDBName = $("#id_query-database").val() 
      
      var AUTOCOMPLETE_BASE_URL = "/beeswax/autocomplete/";

      function autocomplete(options) {
        var _dbbefore = ""
        if (codeMirror != null){
          _dbbefore = codeMirror.getRange({line: 0, ch: 0}, {line: codeMirror.getCursor().line, ch: codeMirror.getCursor().ch}).replace(/(\r\n|\n|\r)/gm, " ");

          if ( _dbbefore.toUpperCase().indexOf("FROM") > -1 && _dbbefore.charAt(_dbbefore.length-1) == '.') {
           currentDBName = getDBName(currentDBName);
           options.database = currentDBName
          }
          else {
           if ( _dbbefore.toUpperCase().indexOf("FROM") > -1 && _dbbefore.charAt(_dbbefore.length-1) != '.') {
            CodeMirror.possibleDatabase = false;
            currentDBName =  $("#id_query-database").val();
            options.database = currentDBName
           }
          }
        }
        if (options.database == null) {
          $.getJSON(AUTOCOMPLETE_BASE_URL, options.onDataReceived);
        }
        if (options.database != null) {
          if (_dbbefore.charAt(_dbbefore.length-1) == '.' && CodeMirror.possibleSoloField == false &&  _dbbefore.toUpperCase().indexOf("FROM") > -1 ) {
              $.getJSON(AUTOCOMPLETE_BASE_URL + options.database + "/", options.onDataReceived);
          }
          else {
            CodeMirror.possibleDatabase = false;
            if (options.table != null) {
              $.getJSON(AUTOCOMPLETE_BASE_URL + options.database + "/" + options.table, options.onDataReceived);
            }
            else {
              $.getJSON(AUTOCOMPLETE_BASE_URL + options.database + "/", options.onDataReceived);
            }
           }
         }
      }

      function getDBName(currentDBName) {
               if(codeMirror!=null) {
                 var _dbefore = codeMirror.getRange({line: 0, ch: 0}, {line: codeMirror.getCursor().line, ch: codeMirror.getCursor().ch}).replace(/(\r\n|\n|\r)/gm, " ");
                 if(_dbefore.charAt(_dbefore.length-1)=='.') {
                  idxFrom = _dbefore.toUpperCase().lastIndexOf(" FROM ");
                  var idxComma = "";
                  var idxDot = "";
                  idxComma = _dbefore.lastIndexOf(",");
                  idxDot = _dbefore.lastIndexOf(".");
                  idxJoin = _dbefore.toUpperCase().lastIndexOf(" JOIN ");
                  idx = Math.max(idxFrom,idxJoin);
                  if(idxComma > idxFrom ) {
                    if(idxJoin > idxComma ) {
                    currentDBName = _dbefore.substring(idxJoin+ 6,idxDot);
                    }
                    else {
                    currentDBName = _dbefore.substring(idxComma+ 1,idxDot);
                    }
                  currentDBName = currentDBName.trim();
                  }
                  else {
                  currentDBName = _dbefore.substr(idx + 6, _dbefore.length-(idx+7) );
                  }
                 }     
                }
                return currentDBName;
      }
      
      function get_DB_Name(table_name) {
              var db_table_name = " ";
              var checking_table_dot1 = " ";
              var checking_table_dot2 = " ";
              db_table_name = table_name;
              checking_table_dot1 = db_table_name.indexOf(".") + 1;
              checking_table_dot2 = db_table_name.indexOf(".");
              table_name = db_table_name.substr(checking_table_dot1);
              currentDBName = db_table_name.substr(0,checking_table_dot2);
              return table_name;
      }

      function getTableAliases() {
        var _aliases = {};
        var _val = codeMirror.getValue();
        var _from = _val.toUpperCase().indexOf("FROM");
        if (_from > -1) {
          var _match = _val.toUpperCase().substring(_from).match(/ON|WHERE|GROUP|SORT/);
          var _to = _val.length;
          if (_match) {
            _to = _match.index;
          }
          var _found = _val.substr(_from, _to).replace(/(\r\n|\n|\r)/gm, "").replace(/from/gi, "").replace(/join/gi, ",").split(",");
          for (var i = 0; i < _found.length; i++) {
            var _tablealias = $.trim(_found[i]).split(" ");
            if (_tablealias.length > 1) {
              _aliases[_tablealias[1]] = _tablealias[0];
            }
          }
        }
        return _aliases;
      }
      

      function getTableColumns(tableName, callback) {
        if (tableName.indexOf("(") > -1) {
            tableName = tableName.substr(tableName.indexOf("(") + 1);
           }
           var _aliases = getTableAliases();
           if (_aliases[tableName]) {
             tableName = _aliases[tableName];
           }
           tableName = get_DB_Name(tableName);
           if (currentDBName == " " || currentDBName == "") {
            currentDBName =  $("#id_query-database").val();
           }      
        if ($.totalStorage('columns_' + currentDBName + '_' + tableName) != null) {
          callback($.totalStorage('columns_' + currentDBName + '_' + tableName));
          autocomplete({
            database: currentDBName,
            table: tableName,
            onDataReceived: function (data) {
              if (data.error) {
                $.jHueNotify.error(data.error);
              }
              else {
                $.totalStorage('columns_' + currentDBName + '_' + tableName, (data.columns ? data.columns.join(" ") : ""));
              }
            }
          });
        }
        else {
          autocomplete({
            database: currentDBName,
            table: tableName,
            onDataReceived: function (data) {
              if (data.error) {
                $.jHueNotify.error(data.error);
              }
              else {
                $.totalStorage('columns_' + currentDBName + '_' + tableName, (data.columns ? data.columns.join(" ") : ""));
                callback($.totalStorage('columns_' + currentDBName + '_' + tableName));
              }
            }
          });
        }
      }

      function tableHasAlias(tableName) {
        var _aliases = getTableAliases();
        for (var alias in _aliases) {
          if (_aliases[alias] == tableName) {
            return true;
          }
        }
        return false;
      }

      function getTables(callback) {
        if ($.totalStorage('tables_' + currentDBName) != null) {
          callback($.totalStorage('tables_' + currentDBName));
          autocomplete({
            database: currentDBName,
            onDataReceived: function (data) {
              if (data.error) {
                $.jHueNotify.error(data.error);
              }
              else {
                $.totalStorage('tables_' + currentDBName, data.tables.join(" "));
              }
            }
          });
        }
        else {
          autocomplete({
            database:  currentDBName,
            onDataReceived: function (data) {
              if (data.error) {
                $.jHueNotify.error(data.error);
              }
              else {
                $.totalStorage('tables_' + currentDBName, data.tables.join(" "));
                callback($.totalStorage('tables_' + currentDBName));
              }
            }
          });
        }
      }

      var queryEditor = $("#queryField")[0];

      getTables(function(){});
       
      var AUTOCOMPLETE_SET = CodeMirror.hiveQLHint;

      CodeMirror.onAutocomplete = function (data, from, to) {
        if (CodeMirror.tableFieldMagic) {
          codeMirror.replaceRange(" ", from, from);
          codeMirror.setCursor(from);
          codeMirror.execCommand("autocomplete");
        }
      };

      CodeMirror.commands.autocomplete = function (cm) {
        tableMagic = false;
        if ($.totalStorage('tables_' + currentDBName) == null) {
          CodeMirror.showHint(cm, AUTOCOMPLETE_SET);        
          getTables(function () {}); // if preload didn't work, tries again
        }
        else {
         var _query_ends = codeMirror.getRange({line: 0, ch: 0}, {line: codeMirror.getCursor().line, ch: codeMirror.getCursor().ch}).replace(/(\r\n|\n|\r)/gm, " ");
         var idx_of_select = "";
         var idx_of_pselect = "";
         var idx_for_select = "";
         idx_of_select = _query_ends.toUpperCase().lastIndexOf(" SELECT ")
         idx_of_pselect = _query_ends.toUpperCase().lastIndexOf("\(SELECT ")
         idx_for_select = Math.max(idx_of_select,idx_of_pselect);
         if (_query_ends.charAt(codeMirror.getCursor().ch - 1) == " " && (_query_ends.toUpperCase().lastIndexOf("FROM") > idx_for_select) ) { 
          currentDBName =  $("#id_query-database").val();
         }
          getTables(function (tables) {
            CodeMirror.catalogTables = tables;
            var _before = codeMirror.getRange({line: 0, ch: 0}, {line: codeMirror.getCursor().line, ch: codeMirror.getCursor().ch}).replace(/(\r\n|\n|\r)/gm, " ");
            CodeMirror.possibleTable = false;
            CodeMirror.tableFieldMagic = false;
            if (_before.toUpperCase().indexOf(" FROM ") > -1 && _before.toUpperCase().indexOf(" ON ") == -1 && _before.toUpperCase().indexOf(" WHERE ") == -1 ) {
             CodeMirror.possibleTable = true;
             CodeMirror.possibleDatabase = false;
             if(_before.charAt(_before.length-1) == ".") {
              if (_before.toUpperCase().lastIndexOf("FROM") < idx_for_select) {
                 CodeMirror.possibleDatabase = false;
                 }
              else{   
                 CodeMirror.possibleDatabase = true;
                 }
             }
            }
            CodeMirror.possibleSoloField = false;
            
            if (_before.toUpperCase().indexOf("SELECT ") > -1 && _before.toUpperCase().indexOf(" FROM ") == -1 && !CodeMirror.fromDot) {
              if (codeMirror.getValue().toUpperCase().indexOf("FROM") > -1) {
                CodeMirror.possibleSoloField = true;
                if(_before.toUpperCase().indexOf("SELECT ") > -1 && _before.toUpperCase().indexOf(" FROM ") == -1 ) {
                  CodeMirror.possibleDatabase = false;
                }
                try {
                  var _possibleTables = $.trim(codeMirror.getValue().substr(codeMirror.getValue().toUpperCase().indexOf("FROM") + 4)).split(" "); 
                  var _foundTable = "";
                  for (var i = 0; i < _possibleTables.length; i++) {
                    if ($.trim(_possibleTables[i]) != "" && _foundTable == "") {
                      _foundTable = _possibleTables[i];
                    }
                  }
                  if (_foundTable != "") {
                    if (tableHasAlias(_foundTable)) {
                      CodeMirror.possibleSoloField = false;
                      CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
                    }
                    else {
                      getTableColumns(_foundTable,
                              function (columns) {
                                CodeMirror.catalogFields = columns;
                                CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
                              });        
                    }
                  }
                }
                catch (e) {
                }
              }
              else {
                CodeMirror.tableFieldMagic = true;
                CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
              }
            }
            else {
              if (CodeMirror.possibleDatabase == false) {
              currentDBName =  $("#id_query-database").val();
              }
              CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
            }
          });
        }
      }

            CodeMirror.fromDot = false;

      codeMirror = CodeMirror.fromTextArea(document.getElementById("queryField"), {
        value: queryEditor.value,
        readOnly: false,
        lineNumbers: true,
        mode: "text/x-hiveql",
        extraKeys: {


         "Ctrl-Space": function () {
            CodeMirror.fromDot = false;
            codeMirror.execCommand("autocomplete");
          },
          Tab: function (cm) {
            $("#executeQuery").focus();
          }
        },
        onKeyEvent: function (e, s) {
          if (s.type == "keyup") {
            if (s.keyCode == 190) {


              var _line = codeMirror.getLine(codeMirror.getCursor().line);
              var _partial = _line.substring(0, codeMirror.getCursor().ch);
              var _table = "";
              var idxofselect = "";
              var idxofpselect = "";
              var idxforselect = "";
              idxofselect = _partial.toUpperCase().lastIndexOf(" SELECT ")
              idxofpselect = _partial.toUpperCase().lastIndexOf("\(SELECT ")
              idxforselect = Math.max(idxofselect,idxofpselect);
              _table = _partial.substring(_partial.lastIndexOf(" ") + 1, _partial.length -1 );
              if (_partial.toUpperCase().indexOf("FROM") > -1 && (_partial.toUpperCase().indexOf(" ON ") == -1 && _partial.toUpperCase().indexOf(" WHERE ") == -1)) { 
                 _table = _partial.substring(_partial.lastIndexOf(" ") + 1, _partial.length);
                 if (_partial.toUpperCase().lastIndexOf("FROM") < idxforselect) {
                 _table = _partial.substring(_partial.lastIndexOf(" ") + 1, _partial.length -1 );
                 }
              } 
               if (codeMirror.getValue().toUpperCase().indexOf("FROM") > -1) {
                 getTableColumns(_table, function (columns) {
                  var _cols = columns.split(" ");
                  for (var col in _cols){
                    _cols[col] = "." + _cols[col];
                  }
                 CodeMirror.catalogFields = _cols.join(" ");
                 CodeMirror.fromDot = true;
                 window.setTimeout(function () { // Commenting it to avoid show hint pop to user on tying just "."
                   codeMirror.execCommand("autocomplete");
                 }, 100);  // timeout for IE8
              });
             }
            }
           }
          }
        });

      codeMirror.on('change',autosave);

      codeMirror.setSize("95%", resizeHeight());

    });
</script>


${ commonfooter(messages) | n,unicode }
