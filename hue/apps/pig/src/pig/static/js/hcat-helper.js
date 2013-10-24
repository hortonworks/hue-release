(function () {

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
          CodeMirror.db_list[database][table]=data;

          $.each(data.columns, function(e){
            if(this.name != "" )
              dirArr.list.push(this.name + ":" + this.type);
          })

          if(dirArr.list.length<2 && dirArr.list.length>0)
            dirArr.list.push("");

          if(dirArr.list.length>0 && dirArr.list[0].name !="")
            showHint(unpickable(dirArr));
        }else{
          delete CodeMirror.db_list[database][table];
        }

      },"json");
    }
    
    //add handler to data to unable pick it
    function unpickable(data) {
      CodeMirror.on(data,'shown',function(widget){
        widget.options.pickoff = true;
      });
      return data;
    }
    // prepare token object
    var cur = cm.getCursor();
    var token = cm.getTokenAt(cur);
    var curText = token.string;

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

      token.className="pig-word";
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
        if (targetLast in CodeMirror.db_list[targetPrev]) {
          if (typeof (CodeMirror.db_list[targetPrev].columns) !== "undefined") {
            $.each(CodeMirror.db_list[targetPrev].columns, function(e){
              if(this.name != "" ){
                fields_hint.push(this.name + ":" + this.type);
                unpickable(dirArr);
              }
            })
          }else{
            return getTableFields(targetLast, targetPrev);
          }
        }
      } else {
        for (var table in CodeMirror.db_list[targetPrev]) {
          maybeAdd('<i class="icon-list-alt"></i> ' + table);
        };
      }
    } else if (targetLast) {
      if (lastKey=='.') {
        if (targetLast in CodeMirror.db_list.default) {
          for (var tablenameD in CodeMirror.db_list.default){
            if (tablenameD == targetLast) {
              if (typeof (CodeMirror.db_list.default[tablenameD].columns) !== "undefined") {
                $.each(CodeMirror.db_list.default[tablenameD].columns, function(e){
                  if(this.name != "" ){
                    fields_hint.push(this.name + ":" + this.type);
                    unpickable(dirArr);
                  }
                })
              } else {
                return getTableFields(targetLast);
              }
            }
          }
        }
        for (var table in CodeMirror.db_list[targetLast]) {
          maybeAdd('<i class="icon-list-alt"></i> ' + table);
        };
      } else {
        for (var dbName in CodeMirror.db_list){
          maybeAdd('<i class="icon-hdd"></i> ' + dbName);
        }
        for (var table in CodeMirror.db_list.default) {
          maybeAdd('<i class="icon-list-alt"></i> ' + table);
        }
      }
    }else{
      for (var dbName in CodeMirror.db_list){
        maybeAdd('<i class="icon-hdd"></i> ' + dbName);
      }
      for (var table in CodeMirror.db_list.default) {
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

})();