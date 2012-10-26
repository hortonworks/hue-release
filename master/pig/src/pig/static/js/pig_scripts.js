function autosave(){
  pig_editor.save();
  python_editor.save()
  $.post("/pig/autosave_scripts/", $("#pig_script_form").serialize());
  return true;
}

var pig_editor = CodeMirror.fromTextArea(document.getElementById("id_pig_script"), {
  lineNumbers: true,
  matchBrackets: true,
  indentUnit: 4,
  mode: "text/x-pig",
  onCursorActivity: function() {
    pig_editor.matchHighlight("CodeMirror-matchhighlight");
  },
  extraKeys: {"Ctrl-Space": function(cm) {CodeMirror.simpleHint(cm, CodeMirror.pigHint);  }},
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
    var lastKeys=from.getLine(from.getCursor().line).substr(from.getCursor().ch-2,2);

    if(lastKeys== "'/" || lastKeys== '"/'){
      var dirList=getDirList(curText);

      var dirArr={
        from: change.from,
        list:dirList,
        to: change.from
      };

      CodeMirror.simpleHint(from, CodeMirror.pigHint, "", dirArr );
    }

    function getDirList(context){
      return ["/dir1","/dir2","/dir3","/dir1/dir_1_1","/dir1/dir_1_2","/dir1/dir_2_1","/dir1/dir_3_1"]
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
  mode: "text/x-python",

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