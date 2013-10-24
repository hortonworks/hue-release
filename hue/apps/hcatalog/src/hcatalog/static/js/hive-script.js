var keywordsT=[];
var keywordsD=[];
var submitFormPopup=false;
CodeMirror.db_list = {};

function getDatabases(){
  $.get("/hcatalog/databases/json" , function(data){
    for (var db in data){
      CodeMirror.db_list[db]= {};
      keywordsD.push('<i class="icon-hdd"></i> ' + db);
      for (var i = data[db].length - 1; i >= 0; i--) {
        CodeMirror.db_list[db][data[db][i]] = {};
        if (db=="default")
          keywordsT.push('<i class="icon-list-alt"></i> ' + data[db][i]);
      };
    }
  },"json");
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
    }
    else {
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
    CodeMirror.showHint(cm, CodeMirror.hint.hCatalog, {'async':true });
  } else {
    CodeMirror.isDir = false;
    CodeMirror.isHCat = false;
    CodeMirror.showHint(cm);
  }
}

var editor = CodeMirror.fromTextArea(document.getElementById("queryField"), {
  lineNumbers: true,
  matchBrackets: true,
  indentUnit: 4,
  mode: "text/x-hive",
  extraKeys: {
    "Ctrl-Space": "autocomplete",
  },
  onKeyEvent: function(cm,key){
    var lineNumber=cm.getCursor().line;
    var curLine=cm.getLine(lineNumber);
    var posArr=findPosition(curLine);

    if(key.keyCode=="9"&&posArr.length>1){
      editor.setOption("keyMap", "emacs");
    }else{
      editor.setOption("keyMap", "basic");
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
    }
    if ((key.keyCode == "222" && /\s/.test(prevKey)) || (key.keyCode == "190" && /\w/.test(prevKey))) {
      CodeMirror.isDir = false;
      CodeMirror.isHCat = true;
      CodeMirror.showHint(cm, CodeMirror.hint.hCatalog, {'async':true });
    }
  }
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

$(document).ready(function(){
  getDatabases();
});
