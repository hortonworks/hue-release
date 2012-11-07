var pigKeywordsT=[];
var dollarSaveParamTrig = 0;
var varSaveParamTrig = 0;

function autosave(){
  $("#save_button").removeAttr("disabled");
  pig_editor.save();
  python_editor.save()
  $.post("/pig/autosave_scripts/", $("#pig_script_form").serialize());
  return true;
}

function listdir(_context){
  console.log("listdir:"+_context);
  // Context - Full path, that user have typed. e.g. /tmp/dir1/
  var contentList=[];
  _context=_context.replace(/'/g, "" ).replace(/"/g, "" );
  _context=_context.split(" ");
  _context=_context[0];


  $.ajax({
    //url: 'files.php/?con=' + _context,
    url: "/proxy/localhost/50070/webhdfs/v1" + _context + "?op=LISTSTATUS&user.name=hue&doas=hdfs",
    type: "GET",
    dataType: "json",
    cache: false,
    async: false,
    success: function(data) {
      //console.log(data);
      if(data.hasOwnProperty("FileStatuses")){
        for (var i = 0; i < data.FileStatuses.FileStatus.length; i++) {
          if(data.FileStatuses.FileStatus[i].pathSuffix !="")
            contentList.push( data.FileStatuses.FileStatus[i].pathSuffix);
        }
      }
    }
  });
  return contentList;
}

function getTables(){
  $.get("/proxy/localhost/50111/templeton/v1/ddl/database/default/table?user.name=hue", function(data){
    //$.get("tables.php", function(data){
    if(data.hasOwnProperty("tables"))
    {
      for (var i = 0; i < data.tables.length; i++) {
        pigKeywordsT.push(data.tables[i]);
      }
    }
  },"json");
}

function getTableFields(table){
  $.get("/proxy/localhost/50111/templeton/v1/ddl/database/default/table/"+table+"?user.name=hue", function(data){
    console.log(data);
  });
}

function changeVarInEditorContent(e){
  console.log(e.currentTarget.id); // = explain
  var html="";
  var editorContent=pig_editor.getValue();
  var found_var=editorContent.match(/\$\S+/g);

  if(found_var != null && found_var.length >0){
    found_var.map(function(elem,i){
      html+='<label>'+elem+':</label><input name="'+elem+'"  /><br/><br/>';
    })
    $(".modal-for-var-input-warp").html( html);

    $("#show-modal-for-var")
        .addClass("cur-"+e.currentTarget.id)
        .modal("show")
        .on('hide', function() {
          if(varSaveParamTrig==1){
            var out_html="";

            $(".modal-for-var-input-warp > input").each(function(){
              out_html+='<input class="var-input-for-form-submit" type="hidden" name="'+$(this).attr("name")+'" value="'+$(this).val()+'" />';
            });
            $(".var-input-for-form-submit").remove();
            $("#pig_script_form").append( out_html );
            $(".modal-for-var-input-warp").html( "" );

            if($("#show-modal-for-var").hasClass("cur-explain"))
              explain_button_click();;

            if($("#show-modal-for-var").hasClass("cur-start_job"))
              start_job_submit_form();
          }
          $("#show-modal-for-var").removeClass("cur-start_job").removeClass("cur-explain");
          varSaveParamTrig=0;
        });

  }
}

function start_job_submit_form(){
  if (!$("#pig_script_form").valid()) return false;
  $("#start_job").hide();
  $("#id_text").attr("disabled", "disabled");
  percent = 2;
  $(".bar").css("width", percent+"%");
  pig_editor.save();
  python_editor.save()
  $.ajax({
    url: "http://ec2-75-101-213-8.compute-1.amazonaws.com:8000/pig/start_job/",
    dataType: "json",
    type: "POST",
    data: $("#pig_script_form").serialize(),
    success: function(data){
      $("#kill_job").show();
      $("#job_info").append(data.text);
      job_id = data.job_id;
      ping_job(job_id);
    }
  });
}

function explain_button_click(){
  if (!$("#pig_script_form").valid()) return false;
  $("#id_text, .explain, #start_job, #kill_job").attr("disabled", "disabled");
  percent = 2;
  $(".bar").css("width", percent+"%");
  var t_s = $(this).attr('value')
  pig_editor.save();
  python_editor.save();
  $.ajax({
    url: "/pig/explain/?t_s=" + t_s,
    dataType: "json",
    type: "POST",
    data: $("#pig_script_form").serialize(),
    success: function(data){
      $("#job_info").text('');
      $("#job_info").append(data.text);
      $("#id_text, .explain, #start_job, #kill_job").removeAttr("disabled");
    }
  });
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
    "Ctrl-Space": function(cm) { CodeMirror.simpleHint(cm, CodeMirror.pigHint);  }/*,
    "Shift-4":function(cm){
      $("#show-modal-for-dollar")
          .modal("show")
          .on('hide', function() {
            if(dollarSaveParamTrig==1){
              cm.replaceRange($("#show-modal-for-dollar").find("input").val(),cm.getCursor()  );
              cm.focus();
            }
            dollarSaveParamTrig=0;
          });
    }*/
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

  },
  onChange : function (from, change){

    var curText=from.getTokenAt(from.getCursor()).string;

    var startKeys=curText.substr(0,2);
    var lastKey=from.getLine(from.getCursor().line).substr(from.getCursor().ch-1,1);
    var prevKey=from.getLine(from.getCursor().line).substr(from.getCursor().ch-2,1);

    if((startKeys== "'/" || startKeys== '"/')&&(lastKey=="/")){
      console.log("change:"+curText)

      var dirList=listdir(curText);

      if(dirList.length<2 && dirList.length>0)
        dirList.push("");

      change.from.ch=from.getCursor().ch;

      var dirArr={
        from: change.from,
        list:dirList,
        to: change.from
      };

      if(dirList.length>0 && dirList[0].trim()!="")
        CodeMirror.simpleHint(from, CodeMirror.pigHint, "", dirArr );

    }else if((prevKey== "'" || prevKey== '"')&&(/\w/.test(lastKey))){

      //change.from.ch=from.getCursor().ch;

      /*var tablesArr={
       from: change.from,
       list: pigKeywordsT,
       to: change.to
       };*/
      // CodeMirror.simpleHint(from, CodeMirror.pigHint, "", tablesArr );

      CodeMirror.simpleHint(from, CodeMirror.pigHint);
    }

    autosave();

  }
});




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



$(".email").bind(
    'change', function(){
      if($(this).attr('checked') == 'checked')
      {$('.intoemail').attr('value', 'checked')}
      else
      {$('.intoemail').attr('value', 'no checked')};
    });
$("#displayText").click(function() {
  var ele = document.getElementById("toggleText");
  var text = document.getElementById("displayText");
  if(ele.style.display == "block") {
    ele.style.display = "none";
  }
  else {
    ele.style.display = "block";
  }
});
$(".udf_register").click(function() {
  $('#id_pig_script').text('REGISTER ' + $(this).attr('value') + '\n' + $('#id_pig_script').val());
  $('.CodeMirror').hide()
  var editor = CodeMirror.fromTextArea(document.getElementById("id_pig_script"), {
    lineNumbers: true,
    matchBrackets: true,
    indentUnit: 4,
    mode: "text/x-pig"
  });
});

function findPosition(curLine){
  var pos= curLine.indexOf("%");
  var posArr=[];
  while(pos > -1) {
    posArr.push(pos);
    pos = curLine.indexOf("%", pos+1);
  }
  return posArr;
}

$("#id_hdfs_file").change(function() {
  str=$("#id_hdfs_file").val().toUpperCase();
  suffix=".JAR";
  if(!(str.indexOf(suffix, str.length - suffix.length) !== -1)){
    alert('File type not allowed,\nAllowed file: *.jar');
    $("#id_hdfs_file").val("");
  }
});


$(document).ready(function(){

  getTables();

  $(".explain").on("click", function(event){
    explain_progres(0);
    changeVarInEditorContent(event);
  });


  $("#start_job").on("click", function(event){
    changeVarInEditorContent(event);
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

  $("#pig_helper").find("a").live('click', function(){
    if($(this).data("python"))
    {
      $("#python_textarea").show();

      python_editor.refresh();
    }
    var cur_val = pig_editor.getValue();
    if (cur_val) cur_val += "\n";
    pig_editor.setValue(cur_val+$(this).text());
    pig_editor.focus();
    //pig_editor.setCursor({line:pig_editor.lineCount(), ch:"0"});

    var pos = findPosition($(this).text());

    if(pos.length>3)
      pig_editor.setOption("keyMap", "emacs");

    if(pos.length>1)
      pig_editor.setSelection({line:pig_editor.lineCount()-1, ch:pos[0]},{line:pig_editor.lineCount()-1, ch:pos[1]+1});

    return false;
  });



  $("#pig_script_form").submit(function(){
    pig_editor.save();
    python_editor.save();
    return true;
  });
});
