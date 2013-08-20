var keywordsT=[];
var submitFormPopup=false;
var db_list = {};

function getDatabases(){
  $.get("/hcatalog/databases/json" , function(data){
    for (var db in data){
      db_list[db]= {};
      for (var i = data[db].length - 1; i >= 0; i--) {
        db_list[db][data[db][i]] = {};
      };
    }
  },"json");
}

function hCatHint (cm, showHint) {

  function maybeAdd(str) {
      var stripped = strip(str).replace(/(?:(?:^|\n)\s+|\s+(?:$|\n))/g,'').replace(/\s+/g,' ');
      if (stripped.indexOf(token.string) == 0 && !arrayContains(fields_hint, str)) fields_hint.push(str);
    }
  
  function strip(html){
    if (jQuery) {
      return $("<div>").html(html).text();
    }
    else {
      var tmp = document.createElement("DIV");
      tmp.innerHTML = html;
      return tmp.textContent || tmp.innerText;
    }
  }

  function arrayContains(arr, item) {
    if (!Array.prototype.indexOf) {
      var i = arr.length;
      while (i--) {
        if (arr[i] === item) {
          return true;
        }
      }
      return false;
    }
    return arr.indexOf(item) != -1;
  }

  function getTableFields(table, database){
    var database = database || 'default';
    $.get("/hcatalog/table/"+database+"/"+table+"/json/", function(data){

      if(typeof (data) !=="undefined" && data.hasOwnProperty("columns") && data.columns.length>0)
      {
        db_list[database][table]=data;

        $.each(data.columns, function(e){
          if(this.name != "" )
            dirArr.list.push(this.name + ":" + this.type);
        })

        if(dirArr.list.length<2 && dirArr.list.length>0)
          dirArr.list.push("");

        if(dirArr.list.length>0 && dirArr.list[0].name !="")
          showHint(dirArr);
      }else{
        delete db_list[database][table];
      }

    },"json");
  }
  // prepare token object
  var cur = cm.getCursor();
  var token = cm.getTokenAt(cm.getCursor());
  var curText=cm.getTokenAt(cm.getCursor()).string;

  if (token.string[0]=="'"||token.string[0]=='"') {

    token.start=token.start+1;
    token.string=token.string.replace("'", "" ).replace('"', "" );

    if (token.string.lastIndexOf("'")>-1||token.string.indexOf('"')>0){
      token.string=token.string.replace(/'/g, "" ).replace(/"/g, "" );
      token.end=token.end-1;
    }

    if (token.string.lastIndexOf(".")>0) {
      token.start=token.start +token.string.lastIndexOf(".")+1 ;
      token.string=token.string.substr(token.string.lastIndexOf(".")+1);
    };

    token.className="hive-word";
  }

  var lastKey=cm.getLine(cm.getCursor().line).substr(cm.getCursor().ch-1,1);
  var targetLast = curText.match(/(\w*)+(\.?)+(\'?)$/)[1];
  var prevMatch = curText.match(/(\w*)(\.)(\w*)/);
  var targetPrev = (prevMatch && prevMatch[3].length>0)?prevMatch[1]:undefined;
  
  var fields_hint = [];


  var dirArr = {list: fields_hint,
                from: CodeMirror.Pos(cur.line, token.start),
                to: CodeMirror.Pos(cur.line, token.end)};

  if (targetPrev) {
    if (lastKey=='.') {
      if (targetLast in db_list[targetPrev]) {
        if (typeof (db_list[targetPrev].columns) !== "undefined") {
          $.each(db_list[targetPrev].columns, function(e){
            if(this.name != "" )
              fields_hint.push(this.name + ":" + this.type);
          })
        }else{
          return getTableFields(targetLast, targetPrev);
        }
      }
    } else {
      for (var table in db_list[targetPrev]) {
        maybeAdd('<i class="icon-list-alt"></i> ' + table);
      };
    }
  } else if (targetLast) {
    if (lastKey=='.') {
      if (targetLast in db_list.default) {
        for (var tablenameD in db_list.default){
          if (tablenameD == targetLast) {
            if (typeof (db_list.default[tablenameD].columns) !== "undefined") {
              $.each(db_list.default[tablenameD].columns, function(e){
                if(this.name != "" )
                  fields_hint.push(this.name + ":" + this.type);
              })
            } else {
              return getTableFields(targetLast);
            }
          }
        }
      }
      for (var table in db_list[targetLast]) {
        maybeAdd('<i class="icon-list-alt"></i> ' + table);
      };
    } else {
      for (var dbName in db_list){
        maybeAdd('<i class="icon-hdd"></i> ' + dbName);
      }
      for (var table in db_list.default) {
        maybeAdd('<i class="icon-list-alt"></i> ' + table);
      }
    }
  }else{
    for (var dbName in db_list){
      maybeAdd('<i class="icon-hdd"></i> ' + dbName);
    }
    for (var table in db_list.default) {
      maybeAdd('<i class="icon-list-alt"></i> ' + table);
    }
  }

  if(fields_hint.length<2 && fields_hint.length>0)
        fields_hint.push(" ");
  if(fields_hint.length>0 && fields_hint[0].name !=""){
    return showHint(dirArr);
  }
      
}

CodeMirror.registerHelper("hint", "hCatalog", hCatHint);

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
