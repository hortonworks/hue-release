var keywordsT=[];
var submitFormPopup=false;
var table_fields={};


function listdir(_context){
  // Context - Full path, that user have typed. e.g. /tmp/dir1/
  var contentList=[];
  _context=_context.replace(/'/g, "" ).replace(/"/g, "" );
  _context=_context.split(" ");
  _context=_context[0];


  $.ajax({
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
      if(keywordsT.length<1){
        for (var i = 0; i < data.tables.length; i++) {
          keywordsT.push(data.tables[i]);
          table_fields[data.tables[i]]={};
        }
      }
    }
  },"json");
}

function getTableFields(table,target){

    $.get("/proxy/localhost/50111/templeton/v1/ddl/database/default/table/"+table+"?user.name=hue", function(data){
    //$.get("table_f.php?con=" + table, function(data){

      if(typeof (data) !=="undefined" && data.hasOwnProperty("columns") && data.columns.length>0)
      {
        table_fields[table]=data;

        $.each(data.columns, function(e){
          if(this.name != "" )
            target.list.push(this.name + ":" + this.type);
        })

        if(target.list.length<2 && target.list.length>0)
          target.list.push("");

        if(target.list.length>0 && target.list[0].name !="")
          CodeMirror.simpleHint(editor, CodeMirror.hiveHint, "", target , true );

      }else{
        delete table_fields[table];
      }

    },"json");

}

var editor = CodeMirror.fromTextArea(document.getElementById("queryField"), {
  lineNumbers: true,
  matchBrackets: true,
  indentUnit: 4,
  mode: "text/x-hive",
  extraKeys: {
    "Ctrl-Space": function(cm) { CodeMirror.simpleHint(cm, CodeMirror.hiveHint);  }
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

  },
  onChange : function (from, change){

    $(".empty-codemirror-textarea-error").remove();

    var curText=from.getTokenAt(from.getCursor()).string;

    var startKeys=curText.substr(0,2);
    var lastKey=from.getLine(from.getCursor().line).substr(from.getCursor().ch-1,1);
    var prevKey=from.getLine(from.getCursor().line).substr(from.getCursor().ch-2,1);

    if((startKeys== "'/" || startKeys== '"/')&&(lastKey=="/"))
    {
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
        CodeMirror.simpleHint(from, CodeMirror.hiveHint, "", dirArr );

    }
    else if((prevKey== "'" || prevKey== '"')&&(/\w/.test(lastKey)))
    {
      CodeMirror.simpleHint(from, CodeMirror.hiveHint);
    }
    else if(lastKey == "." )
    {
      var table_name=from.getLine(from.getCursor().line).substr(0,from.getCursor().ch-1);
      table_name=table_name.match(/\w*$/);
      if(table_name!="")
      {
        var fields_hint=[];

        change.from.ch=from.getCursor().ch;

        var dirArr={
          from: change.from,
          list:fields_hint,
          to: change.from
        };

        $.each(table_fields, function(e){
          if(e == table_name)
          {
            if(typeof (this.columns) !== "undefined")
            {
              $.each(this.columns, function(e){
                if(this.name != "" )
                  fields_hint.push(this.name + ":" + this.type);
              })
            }else{
              getTableFields(e, dirArr);
            }
          }
        })

        if(fields_hint.length<2 && fields_hint.length>0)
          fields_hint.push("");

        if(fields_hint.length>0 && fields_hint[0].name !=""){
          CodeMirror.simpleHint(from, CodeMirror.hiveHint, "", dirArr , true );
        }
      }
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
  getTables();
});
