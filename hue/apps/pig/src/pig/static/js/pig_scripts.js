var dollarSaveParamTrig = 0;
var varSaveParamTrig = 0;
var submitFormPopup=false;
var table_fields={};
var tmpDirList={path:"",list:[]};
CodeMirror.db_list = {};


function ping_job(job_id){
  var url = '/pig/ping_job/';
  $.get(url+job_id + "/",
      function(data) {
        if (data.exitValue !== null)
        {
          if (data.status.failureInfo != 'NA')
            $("#failure_info").html(data.status.failureInfo);
	  	percent += 0.5;
		$(".bar").css("width", percent+"%");
	        globalTimer = window.setTimeout("get_job_result('"+job_id+"');", 8000);
          return
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
        globalTimer = window.setTimeout("ping_job('"+job_id+"');", 200);
      }, "json");

    $("#kill_job").unbind('click');
    $("#kill_job").click(function(){
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

  var d = $.Deferred();

  setInterval(function() {
    if(submitFormPopup==true) {
      //submitFormPopup=false;
      return  d.resolve();
    }
    else{
      return d.promise();
    }
  }, 100);

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
      return d.promise();
  }

  var html="";
  var editorContent=pig_editor.getValue();
  var found_var=editorContent.match(/\%\S+\%/g);

  if(found_var != null && found_var.length >0){
    found_var.map(function(elem,i){
      html+='<label>'+elem.slice(1,elem.length-1)+':</label><input name="'+elem+'"  /><br/><br/>';
    })
    $(".modal-for-var-input-warp").html( html );
    $("#show-modal-for-var").modal("show");
  }else{
    submitFormPopup=true;
  }
  return d.promise();
}

function autosave(){
  $("#save_button").removeAttr("disabled");
  pig_editor.save();
  python_editor.save()
  $.post("/pig/autosave_scripts/", $("#pig_script_form").serialize());
  return true;
}

$("#show-modal-for-var").on('hide', function() {
  if(varSaveParamTrig==1){
    var out_html="";
    $(".modal-for-var-input-warp > input").each(function(){
      if($(this).val().trim()!=""){
        out_html+='<input class="var-input-for-form-submit" type="hidden" name="'+$(this).attr("name")+'" value="'+$(this).val()+'" />';
      }else{
        out_html="";
        return false;
      }
    });
    if(out_html!=""){
      $(".var-input-for-form-submit").remove();
      $("#pig_script_form").append( out_html );
      $(".modal-for-var-input-warp").html( "" );
      submitFormPopup=true;
    } else {
      varSaveParamTrig=0;
      $(".modal-for-var-input-warp > input").each(function(){
        if($(this).val().trim()=="")
          $(this).css("border","solid 1px red");
        $(".var-input-for-form-submit").remove();
      })
      submitFormPopup=false;
      return false;
    }
  } else {
    $(".var-input-for-form-submit").remove();
    $(".modal-for-var-input-warp").html( "" );
    submitFormPopup=false;
  }
  varSaveParamTrig=0;
});

function getDatabases(){
  $.get("/hcatalog/databases/json" , function(data){
    for (var db in data){
      CodeMirror.kwset.db.push('<i class="icon-hdd"></i> ' + db)
      CodeMirror.db_list[db]= {};
      for (var i = data[db].length - 1; i >= 0; i--) {
        CodeMirror.db_list[db][data[db][i]] = {};
        CodeMirror.kwset.tables.push('<i class="icon-list-alt"></i> ' + data[db][i])
        $("#hcatalog_helper").append($("<li><a href='#'>LOAD '" + db + "." + data[db][i] + "' USING org.apache.hcatalog.pig.HCatLoader();</a></li>"));
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
          $("#hcatalog_helper").append($("<li><a href='#'>LOAD '" + database + "." + data[i] + "' USING org.apache.hcatalog.pig.HCatLoader();</a></li>"));
        }
      }

  },"json");
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
  onCursorActivity: function() {
    pig_editor.matchHighlight("CodeMirror-matchhighlight");
  },
  extraKeys: {
    "Ctrl-Space": "autocomplete",
  },
  onKeyEvent: function(cm,key){
    var lineNumber=cm.getCursor().line;
    var curLine=cm.getLine(lineNumber);
    var posArr=findPosition(curLine);

    if(key.keyCode=="9"&&posArr.length>1){
      pig_editor.setOption("keyMap", "emacs");
    }else{
      pig_editor.setOption("keyMap", "basic");
    }

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

pig_editor.on('change',function (){autosave();});

var python_editor = CodeMirror.fromTextArea(document.getElementById("python_code"), {
  mode: {name: "python",
    version: 2,
    singleLineStringErrors: true},
  lineNumbers: true,
  indentUnit: 4,
  smartIndent: true,
  tabMode: "shift",
  matchBrackets: true,
  onChange: autosave,
  mode: "text/x-python"
});

$('.script_label').on('click',function(e){
  if (e.target.tagName.toLowerCase() == 'i'){
    return false;
  } else if ($(this).attr('for')=="id_pig_script") {
    $(pig_editor.getWrapperElement()).toggle();
  } else if ($(this).attr('for')=="python_code") {
    $(python_editor.getWrapperElement()).toggle();
  }
})

function findPosition(curLine){
  var pos= curLine.indexOf("%");
  var posArr=[];
  while(pos > -1) {
    posArr.push(pos);
    pos = curLine.indexOf("%", pos+1);
  }
  return posArr;
}

function paginator(lines_per_page){

  var lines = $("#job_info").text().split("\n");
  if(lines.length < lines_per_page)
  {
    return;
  }

  $("#job_info_outer").append("<div class='pagination_controls'></div>");
  $(".pagination_controls").pagination(lines.length, {
    items_per_page:lines_per_page,
    callback:handlePaginationClick
  });

  $("#job_info_outer").css({
    "padding-bottom" : "30px"
  })

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

$(document).ready(function(){

  paginator(30);

  getTables();

  $(".email").change(
      function(){
      if($(this).attr('checked') == 'checked')
      {$('.intoemail').attr('value', 'checked')}
      else
      {$('.intoemail').attr('value', 'no checked')};
    });

  var uploader = new qq.FileUploader({
          //debug: true,
          element: document.getElementById('udf_file_upload'),
          allowedExtensions: ["jar"],
          action: $("#udfs_form").attr("action"),
          multiple: false,
          template: '<div class="qq-uploader">'+
                    '<div class="qq-upload-drop-area"><span></span></div>' +
                    '<div class="qq-upload-button"><i class="icon-upload icon-white"></i> Upload UDF Jar </div>' +
                    '<ul class="qq-upload-list"></ul>' +
                    '</div>',
          params:{
            dest: $("#udfs_form").data("destination"),
            fileFieldLabel:"hdfs_file"
          },
          onComplete:function (id, fileName, response) {
            if (response.status != 0) {
              $.jHueNotify.error("Error: " + (response['error'] ? response['error'] : " occured. Please check udf_path setting in hue.ini" ));
            } else {
                $.jHueNotify.info("UDF was successfully uploaded");
                setTimeout("window.location.reload(true)", 1000);
            }
          },
  });


  $(".udf_register").click(function() {
      pig_editor.setValue('REGISTER ' + $(this).attr('value') + '\n'+ pig_editor.getValue());
  
  });
  
  $("#save_button").live("click", function(){
   if(percent > 0 && percent < 100) return confirm("Job is running. Are you sure, you want to switch to edit mode?");
  });


  $("#save-param-modal-for-dollar").click(function(){
    dollarSaveParamTrig=1;
    $("#show-modal-for-dollar").modal("hide");
  })

  $("#save-values-for-var").click(function(){
    varSaveParamTrig=1;
    $("#show-modal-for-var").modal("hide");
  })

  $("#id_title").live('keyup', autosave);

  $("#pig_helper").find(".dropdown-menu").find("a").live('click', function(){
    if($(this).data("python"))
    {
      $("#python_textarea").show();

      python_editor.refresh();
    }
    var cursor = pig_editor.getCursor();
    pig_editor.replaceRange($(this).text(), cursor, cursor)
    pig_editor.focus();
    //pig_editor.setCursor({line:pig_editor.lineCount(), ch:"0"});

    var pos = findPosition($(this).text());

    if(pos.length>3)
      pig_editor.setOption("keyMap", "emacs");

    if(pos.length>1)
      pig_editor.setSelection({line:cursor['line'], ch:cursor['ch'] + pos[0]},
        {line:cursor['line'], ch:cursor['ch'] + pos[1]+1});

    return false;
  });



  $("#pig_script_form").submit(function(){
    pig_editor.save();
    python_editor.save();
    return true;
  });
});
