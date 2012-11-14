  var pigKeywordsT=[];
  function getTables(){
    var Keywords=[];
    $.get("/proxy/localhost/50111/templeton/v1/ddl/database/default/table?user.name=hue", function(data){
      if(data.hasOwnProperty("tables"))
      {
        for (var i = 0; i < data.tables.length; i++) {
          Keywords.push(data.tables[i]);
        }
      }
    },"json");
    return Keywords;
  }

      var editor = CodeMirror.fromTextArea(document.getElementById("queryField"), {
            lineNumbers: true,
      	    matchBrackets: true,
	    indentUnit: 4,
	    mode: "text/x-mysql",
	    onChange : function (from, change){
                var curText=from.getTokenAt(from.getCursor()).string;
 	        var startKeys=curText.substr(0,1);
	        var lastKey=from.getLine(from.getCursor().line).substr(from.getCursor().ch-1,1);
                var prevKey=from.getLine(from.getCursor().line).substr(from.getCursor().ch-2,1);
                if((startKeys== "'" || startKeys== '"')&&(/\s/.test(prevKey))){
                    var dirList=getTables();
                    if(dirList.length<2)
                        dirList.push("");
                    change.from.ch=from.getCursor().ch;
	            var dirArr={
                      from: change.from,
                      list:dirList,
                      to: change.from
                    };
	            if(dirList.length>0)
                      CodeMirror.simpleHint(from, CodeMirror.pigHint, "", dirArr );
                } else if((prevKey== "'" || prevKey== '"')&&(/\w/.test(lastKey))){
                    CodeMirror.simpleHint(from, CodeMirror.pigHint);
                }
            }
      });

