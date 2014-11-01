var templetonJobRunStates = {RUNNING:1, SUCCEEDED:2, FAILED:3, PREP:4, KILLED:5};
CodeMirror.db_list = {};

function ping_job(job_id){
  var url = '/pig/ping_job/';
  var timeToGetJobResults = false;
  var get_ping = $.get(url+job_id + "/",
    function(data) {
      if (data.exitValue !== null){
        if (data.status.failureInfo != 'NA'){
          $("#failure_info").removeClass('hide').html(data.status.failureInfo);
        }
        timeToGetJobResults = true;
      }
      if (data.status.runState == templetonJobRunStates.KILLED){
        $("#failure_info").removeClass('hide').html("Job " + job_id + " was failed");
        if (percent < 90){
          percent = 90;
        }
        timeToGetJobResults = true;
      }
      else if (data.status.runState == templetonJobRunStates.FAILED ||
          (data.completed && data.exitValue != null && data.exitValue != 0)){
        $("#failure_info").removeClass('hide').html("Job " + job_id + " was failed");
        timeToGetJobResults = true;
      }
      if(timeToGetJobResults)
      {
        percent += 0.5;
        $(".bar").css("width", percent+"%");
        globalTimer = window.setTimeout("get_job_result('"+job_id+"');", 8000);
        return;
      }


      if (/[1-9]\d?0?\%/.test(data.percentComplete))
      {
        var job_done = parseInt(data.percentComplete.match(/\d+/)[0]);
        if (job_done==100) job_done=90
        percent = (job_done < percent)?percent:job_done;
        $(".bar").css("width", percent + "%");
      }
      else
      {
	    if (percent < 3)
        percent += 1;
        $(".bar").css("width", percent+"%");
      }
      globalTimer = window.setTimeout("ping_job('"+job_id+"');", 2000);
    }, "json");

    $("#kill_job").unbind('click');
    $("#kill_job").click(function(){
        get_ping.abort();
        clearTimeout(globalTimer);
        $(this).hide();
        $("#id_text").removeAttr("disabled");
        $(".action_btn").show();
        percent = 0;
        $(".bar").css("width", percent+"%");
        $.post("/pig/kill_job/",{job_id: job_id}, function(data){
            $("#job_info").append("<br>"+data.text);
        }, "json");
    });
}

function call_popup_var_edit(){

  var deffer = $.Deferred();

  if(!pig_editor.getValue())
  {
      $(".empty-codemirror-textarea-error").remove();
      $(".CodeMirror").append("<div class='empty-codemirror-textarea-error'>This field is required.</div>");
      $(".empty-codemirror-textarea-error").css({
          "padding":"15px 0px",
          "color":"red",
          "font-size":"14px",
          "font-weight":"bold"
      });
      setTimeout(function(){pig_editor.focus();}, 50);
      return deffer.promise();
  }

  var html="",found_var;
  var editorContent=pig_editor.getValue();
  var match_var=editorContent.match(/\%\w+\%/g);

  if(match_var != null && match_var.length >0){
    found_var=match_var.filter(function(elem, pos) {
      return match_var.indexOf(elem) == pos;
    });
    found_var.map(function(elem,i){
      html+='<label>'+elem.slice(1,elem.length-1)+':</label><input name="'+elem+'"  /><br/><br/>';
    })
    $(".modal-for-var-input-warp").html( html );
    $("#show-modal-for-var").modal("show");
    $('#save-values-for-var').unbind('click').bind('click', function () {
      return modVarInput(deffer);
    });
  } else {
    return deffer.resolve();
  }
  return deffer.promise();
}

function autosave(){
  $("#save_button").removeAttr("disabled");
  pig_editor.save();
  python_editor.save()
  $.post("/pig/autosave_scripts/", $("#pig_script_form").serialize());
  return true;
}

function modVarInput(deffer) {
    var out_html="";
    $(".modal-for-var-input-warp > input").each(function(){
      if($(this).val().trim()!=""){
        out_html+='<input class="var-input-for-form-submit" type="hidden" name="'+$(this).attr("name")+'" value="'+$(this).val()+'" />';
      }else{
        out_html="";
        return deffer.promise();
      }
    });
    if(out_html!=""){
      $(".var-input-for-form-submit").remove();
      $("#pig_script_form").append( out_html );
      $(".modal-for-var-input-warp").html( "" );
      $("#show-modal-for-var").modal("hide");
      return deffer.resolve();
    } else {
      $(".modal-for-var-input-warp > input").each(function(){
        if($(this).val().trim()=="")
          $(this).css("border","solid 1px red");
        $(".var-input-for-form-submit").remove();
      })
      return deffer.promise();
    }
}

function getDatabases(){
  $.get("/hcatalog/databases/json" , function(data){
    for (var db in data){
      CodeMirror.kwset.db.push('<i class="icon-hdd"></i> ' + db)
      CodeMirror.db_list[db]= {};
      for (var i = data[db].length - 1; i >= 0; i--) {
        CodeMirror.db_list[db][data[db][i]] = {};
        CodeMirror.kwset.tables.push('<i class="icon-list-alt"></i> ' + data[db][i])
        $("#hcatalog_helper").append($("<li><a href='#'>LOAD '" + db + "." + data[db][i] + "' USING org.apache.hive.hcatalog.pig.HCatLoader();</a></li>"));
      };
    }
  },"json");
}

function getTables(database){
  var database = database || 'default';
  $.get("/hcatalog/tables/json/" + database, function(data){
      if(CodeMirror.kwset.tables.length<1){
        for (var i = 0; i < data.length; i++) {
          CodeMirror.kwset.tables = CodeMirror.kwset.tables.concat(data[i]); //pigKeywordsT.push(data[i]);
          CodeMirror.db_list[database][data[i]]={};
          $("#hcatalog_helper").append($("<li><a href='#'>LOAD '" + database + "." + data[i] + "' USING org.apache.hive.hcatalog.pig.HCatLoader();</a></li>"));
        }
      }

  },"json");
}

CodeMirror.toggleEditor = function (mode,editor) {
  var mode = mode || '';
  var piged = editor == 'pig';
  var pyed = editor == 'python';
  var pigwrap = $(pig_editor.getWrapperElement());
  var pythonwrap = $(python_editor.getWrapperElement());
  if (mode=='show') {
    if (!pigwrap.is(":visible") && !pyed) pigwrap.toggle('fast',pig_editor.refresh);
    if (!pythonwrap.is(":visible") && !piged) pythonwrap.toggle('fast');
  } else if (mode=='hide') {
    if (pigwrap.is(":visible") && !pyed) pigwrap.toggle('fast');
    if (pythonwrap.is(":visible") && !piged) pythonwrap.toggle('fast');
  } else {
    if (!pyed) pigwrap.toggle('fast',function  () {
      if (pigwrap.is(":visible")) pig_editor.refresh(); 
    });
    if (!piged) pythonwrap.toggle('fast');
  }
}


CodeMirror.commands.autocomplete = function (cm) {
  $(document.body).on("contextmenu", function (e) {
    e.preventDefault(); // prevents native menu on FF for Mac from being shown
  });
  var curText=cm.getTokenAt(cm.getCursor()).string;
  var startKeys=curText.substr(0,2);
  var lastKey=cm.getLine(cm.getCursor().line).substr(cm.getCursor().ch-1,1);
  var prevKey=cm.getLine(cm.getCursor().line).substr(cm.getCursor().ch-2,1);
  if ((startKeys== "'/" || startKeys== '"/')) {
    CodeMirror.isDir = true;
    CodeMirror.isHCat = false;
    if (lastKey=='/') {
      showHdfsHint(cm, curText);
    } else {
      showHdfsHint(cm, curText.substring(0,curText.lastIndexOf('/')+1));
    }
  } else if (curText.lastIndexOf("'")==0 || (curText.lastIndexOf("'")== curText.length-1 && cm.getTokenAt(cm.getCursor()).end!=cm.getCursor().ch)) {
    CodeMirror.isDir = false;
    CodeMirror.isHCat = true;
    CodeMirror.showHint(cm, CodeMirror.hint.hCatalog, {'async':true});
  } else {
    CodeMirror.isDir = false;
    CodeMirror.isHCat = false;
    CodeMirror.showHint(cm);
  }
}

function showHdfsHint(codeMirror, path_) {
  CodeMirror.listDir = [];
  var path=path_.replace(/'/g, "" ).replace(/"/g, "" );
      path=path.split(" ");
      path="/filebrowser/view" + path[0];
  $.post(path, null,function (data) {
    CodeMirror.listDir = [];
    if (data.error != null) {
      $.jHueNotify.error(data.error);
      CodeMirror.listDir.length = 0;
    } else {
      $(data.files).each(function (cnt, item) {
        itm_name = item.name;
        if (itm_name != ".") {
          var _ico = "icon-file";
          if (item.type == "dir") {
            _ico = "icon-folder-close";
          }
          CodeMirror.listDir.push('<i class="' + _ico + '"></i> ' + itm_name);
        }
      });
      window.setTimeout(function () {
        CodeMirror.showHint(codeMirror);
      }, 100);  // timeout for IE8
    }
  },'json');
}

var pig_editor = CodeMirror.fromTextArea(document.getElementById("id_pig_script"), {
  lineNumbers: true,
  matchBrackets: true,
  indentUnit: 4,
  mode: "text/x-pig",
  highlightSelectionMatches: {
    style: "CodeMirror-matchhighlight"
  },
  extraKeys: {
    "Ctrl-Space": "autocomplete",
  },
  keyMap: "emacs",
  onKeyEvent: function(cm,key){
    // filter keyup events
    if (key.type!="keyup") return;

    $(".empty-codemirror-textarea-error").remove();
    
    // get current string
    var curText=cm.getTokenAt(cm.getCursor()).string;

    var startKeys=curText.substr(0,2);
    var lastKey=cm.getLine(cm.getCursor().line).substr(cm.getCursor().ch-1,1);
    var prevKey=cm.getLine(cm.getCursor().line).substr(cm.getCursor().ch-2,1);

    var _line = cm.getLine(cm.getCursor().line);
    var _partial = _line.substring(0, cm.getCursor().ch);

    if (key.keyCode=="191" && (startKeys== "'/" || startKeys== '"/')) {
      CodeMirror.isDir = true;
      CodeMirror.isHCat = false;
      showHdfsHint(cm, curText);
    } else if ((key.keyCode == "222" && /\s/.test(prevKey)) || (key.keyCode == "190" && /\w/.test(prevKey))) {
      CodeMirror.isDir = false;
      CodeMirror.isHCat = true;
      CodeMirror.showHint(cm, CodeMirror.hint.hCatalog, {'async':true });
    }
  }
});
pig_editor.setSize("", ($(window).height()>=550)?$(window).height()-350:200);

var python_editor = CodeMirror.fromTextArea(document.getElementById("python_code"), {
  mode: {name: "python",
    version: 2,
    singleLineStringErrors: true},
  lineNumbers: true,
  indentUnit: 4,
  smartIndent: true,
  tabMode: "shift",
  matchBrackets: true,
  mode: "text/x-python"
});

var resizeTimeout = -1;
var winWidth = 0;
var winHeight = 0;

function resizeCM () {
  window.clearTimeout(resizeTimeout);
  resizeTimeout = window.setTimeout(function () {
    // prevents endless loop in IE8
    if (winWidth != $(window).width() || winHeight != $(window).height()) {
      pig_editor.setSize("", ($(window).height()>=550)?$(window).height()-350:200);
      winWidth = $(window).width();
      winHeight = $(window).height();
    }
  }, 200);
}

python_editor.on('change',autosave);
pig_editor.on("change", autosave);
$(window).resize(resizeCM);

$('.script_label').on('click',function(e){
  if (e.target.tagName.toLowerCase() == 'i'){
    return false;
  } else if ($(this).attr('for')=="id_pig_script") {
    CodeMirror.toggleEditor('','pig')
  } else if ($(this).attr('for')=="python_code") {
    CodeMirror.toggleEditor('','python')
  }
})

function paginator(lines_per_page){

  var lines = $("#job_info").text().split("\n");
  if(lines.length < lines_per_page)
  {
    return;
  }

  $("#job_info_outer").removeClass('hide')
    .append("<div class='pagination_controls'></div>")
    .css({"padding-bottom" : "30px"});
  $(".pagination_controls").pagination(lines.length, {
    items_per_page:lines_per_page,
    callback:handlePaginationClick
  });


  function handlePaginationClick(new_page_index, pagination_container) {
    //debugger;
    // This selects 20 elements from a content array
    var i=new_page_index*lines_per_page;
    var max= i+lines_per_page;

    $("#job_info").html("");
    for(i;i<max;i++) {
      if(i<lines.length)
      {
        $('#job_info').append(lines[i]+"\n");
      }else{
        $('#job_info').append("\n");
      }

    }
    return false;
  }

};

function findPosition(curLine){
  var pos= curLine.indexOf("%");
  var posArr=[];
  while(pos > -1) {
    posArr.push(pos);
    pos = curLine.indexOf("%", pos+1);
  }
  return posArr;
}

$(document).ready(function(){

  paginator(30);

  getDatabases();

  $(".email").change(
    function(){
    if($(this).attr('checked') == 'checked')
    {$('.intoemail').attr('value', 'checked')}
    else
    {$('.intoemail').attr('value', 'no checked')};
  });

  var Udf = function (data) {
    this.id = ko.observable(data.id);
    this.file_name = ko.observable(data.file_name);
  }

  var viewModel = function () {
    var self = this;
    self.udflist = ko.observableArray([]);
    self.get_url = $('.get_udf_url').val();
    self.del_url = $('.del_udf_url').val().substr(0,$('.del_udf_url').val().length-1);
    self.selectedUdf = ko.observable();

    self.loadUdfs = function(){
      self.udflist([])
      $.getJSON(self.get_url, function (data) {
        $.each(data,function (id,name) {
          self.udflist.push(new Udf({id:id,file_name:name}));
        })
      });
    }

    self.rmUdf = function (udf) {
      self.selectedUdf = udf;
      $('#udfRmConfirm').modal('show');
    }

    self.rm_confirm = function  () {
      var udf = self.selectedUdf;
      $.post(self.del_url+udf.id()+'/',function  (response) {
        $('#udfRmConfirm').modal('hide');
        if (response.status==0) {
          self.udflist.remove(udf);
          $.jHueNotify.info(response.message);
        } else {
          $.jHueNotify.error(response.message);
        }
      },'json').error(function(){
        $.jHueNotify.error("UDF not found");
      });
    }

    self.putToEditor = function (udf) {
      pig_editor.setValue('REGISTER ' + udf.file_name() + '\n'+ pig_editor.getValue());
    }

    self.uploader = new qq.FileUploader({
          //debug: true,
          element: document.getElementById('udf_file_upload'),
          allowedExtensions: ["jar"],
          action: $("#udfs_form").attr("action"),
          multiple: false,
          template: '<div class="qq-uploader">'+
                    '<div class="qq-upload-drop-area"><span>Drop files here to upload</span></div>' +
                    '<div class="qq-upload-button"><i class="icon-upload icon-white"></i> Upload UDF Jar </div>' +
                    '<ul class="qq-upload-list"></ul>' +
                    '</div>',
          params:{
            dest: $("#udfs_form").data("destination"),
            fileFieldLabel:"hdfs_file"
          },
          onComplete:function (id, fileName, response) {
            if (response.status != 0) {
              if (!response.error) $.jHueNotify.error("Error: occured. Please check udf_path setting in hue.ini" );
            } else {
                self.udflist.push(new Udf({id:response.udf_id,file_name:fileName}));
                $.jHueNotify.info("UDF was successfully uploaded");
            }
          },
          showMessage: function(msg){
            $.jHueNotify.error("Error: " + msg);
          }
    });

    self.loadUdfs();

  }

  ko.applyBindings(new viewModel());
  
  $("#save_button").live("click", function(){
    if(percent > 0 && percent < 100) {
      $("#onRunJobSave").modal("show");
      return false;
    }
  });

  $('#runningJobSaveBtn').click(function(){$("#pig_script_form").submit()});

  $("#id_title").live('keyup', autosave);

  $("#pig_helper").find(".dropdown-menu").find("a").live('click', function(){
    if($(this).data("python"))
    {
      $("#python_textarea").show();

      python_editor.refresh();
    }
    var cursor = pig_editor.getCursor();
    pig_editor.replaceRange($(this).text(), cursor, cursor);
    pig_editor.focus();
    //pig_editor.setCursor({line:pig_editor.lineCount(), ch:"0"});

    var pos = findPosition($(this).text());

    //if(pos.length>3)
      //pig_editor.setOption("keyMap", "emacs");

    if (pos.length>1) {
      pig_editor.setSelection({line:cursor.line, ch:cursor.ch + pos[0]},
                              {line:cursor.line, ch:cursor.ch + pos[1]+1});}

    return false;
  });



  $("#pig_script_form").submit(function(){
    pig_editor.save();
    python_editor.save();
    return true;
  });

    
});
