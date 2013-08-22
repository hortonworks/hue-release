(function () {
  function forEach(arr, f) {
    for (var i = 0, e = arr.length; i < e; ++i) f(arr[i]);
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

  function scriptHint(editor, keywords, getToken) {
    // Find the token at the cursor
    var cur = editor.getCursor();
    var token = getToken(editor, cur);

    if(token.string[0]=="'"||token.string[0]=='"'){

      token.start=token.start+1;
      token.string=token.string.replace("'", "" ).replace('"', "" );

      if(token.string.lastIndexOf("'")>0||token.string.indexOf('"')>0){
        token.string=token.string.replace(/'/g, "" ).replace(/"/g, "" );
        token.end=token.end-1;
      }

      token.className="hive-word";
    }

    if (token.string.indexOf("/")> -1) {
      token.string = token.string.substring(token.string.lastIndexOf("/") + 1);
    };


    var tprop = token;
    // If it's not a 'word-style' token, ignore the token.

    if (!/^[\w$_]*$/.test(token.string)) {
      token = tprop = {start: cur.ch, end: cur.ch, string: "", state: token.state,
        className: token.string == ":" ? "hive-type" : null};
    }

    if (!context) var context = [];
    context.push(tprop);

    var completionList = getCompletions(token, context);
    completionList = completionList.sort();
    //prevent autocomplete for last word, instead show dropdown with one word
    if(completionList.length == 1) {
      completionList.push(" ");
    }

    return {list: completionList,
      from: {line: cur.line, ch: token.start},
      to: {line: cur.line, ch: token.end}};
  }

  CodeMirror.registerHelper("hint", "hive", function(editor) {
    return scriptHint(editor, keywordsU, function (e, cur) {return e.getTokenAt(cur);});
  });

  function toTitleCase(str) {
    return str.replace(/(?:^|\s)\w/g, function(match) {
      return match.toUpperCase();
    });
  }

  CodeMirror.listDir = [];
  CodeMirror.isHCat = false;
  CodeMirror.isDir = false;

  var keywords = "CREATE\tDATABASE\tSCHEMA\tTABLE\tEXTERNAL\tIF\tNOT\tEXISTS\tCOMMENT\tLOCATION\t" 
	  + "WITH\tDBPROPERTIES\tDROP\tRESTRICT\tCASCADE\tPARTITIONED BY\tCLUSTERED BY\tSORTED BY\t" 
	  + "ASC\tDESC\tINTO\tBUCKETS\tSKEWED BY\tON\tROW FORMAT\tSTORED AS\tSTORED BY\tBY\t" 
	  + "WITH SERDEPROPERTIES\tTBLPROPERTIES\tLIKE\tDELIMITED\tFIELDS TERMINATED BY\t"
	  + "COLLECTION ITEMS TERMINATED BY\tMAP KEYS TERMINATED BY\tLINES TERMINATED BY\tSERDE\t"
	  + "SEQUENCEFILE\tTEXTFILE\tRCFILE\tINPUTFORMAT\tOUTPUTFORMAT\tAS\tCLUSTER BY\tSORT BY\t"
	  + "IF EXISTS\tIF NOT EXISTS\tALTER\tADD\tPARTITION\tMSCK\tREPAIR\tRECOVER\tPARTITIONS\t"
	  + "RENAME TO\tCHANGE\tCOLUMN\tFIRST\tAFTER\tREPLACE COLUMNS\tSET\tSET TBLPROPERTIES\t"
	  + "SET SERDE\tSET SERDEPROPERTIES\tSET FILEFORMAT\tSET LOCATION\tTOUCH\tARCHIVE PARTITION\t"
	  + "UNARCHIVE PARTITION\tENABLE\tDISABLE NO_DROP\tDISABLE OFFLINE\tRENAME TO PARTITION\t"
	  + "VIEW\tLOAD\tINSERT\tFROM\tWHERE\tTEMPORARY\tFUNCTION\tINDEX\tWITH DEFERRED REBUILD\t"
	  + "IDXPROPERTIES\tSHOW\tDATABASES\tSCHEMAS\tTABLES\tEXTENDED\tFUNCTIONS\tFORMATTED\tINDEXES\t"
	  + "IN\tCOLUMNS\tDOT\tDESCRIBE\tLOCK\tTABLESAMPLE\tUNION\tUNION ALL\tLATERAL\tLATERAL VIEW\t"
	  + "JOIN\tLEFT\tRIGHT\tFULL\tOUTER\tSEMI\tCROSS\tCROSS JOIN\tMAPJOIN\tSTREAMTABLE\tALL\t"
	  + "DISTINCT\tDISTRIBUTE BY\tGROUP BY\tLIMIT\tAND\tOR\tHAVING\tLOAD DATA\tINPATH\t"
	  + "SELECT\tIMPORT\tEXPORT\tINPUT__FILE__NAME\tBLOCK__OFFSET__INSIDE__FILE\tEXPLAIN\tOVERWRITE\t"
	  + "CREATE ROLE\tDROP ROLE\GRANT ROLE\tREVOKE ROLE\tUSER\tGROUP\tROLE\tGRANT\tSHOW ROLE GRANT\t";
  var keywordsU = keywords.split("\t");
  var keywordsL = keywords.toLowerCase().split("\t");

  var types = "TINYINT SMALLINT INT BIGINT BOOLEAN FLOAT DOUBLE STRING BINARY TIMESTAMP ARRAY MAP STRUCT UNIONTYPE";
  var typesU = types.split(" ");
  var typesL = types.toLowerCase().split(" ");

  var builtins ="ABS AVG MAX MIN DISTINCT";
  var builtinsU = builtins.split(" ").join("() ").split(" ");
  var builtinsL = builtins.toLowerCase().split(" ").join("() ").split(" ");

  function getCompletions(token, context) {
    var found = [], start = token.string;
    function maybeAdd(str) {
      var stripped = strip(str).replace(/(?:(?:^|\n)\s+|\s+(?:$|\n))/g,'').replace(/\s+/g,' ');
      if (stripped.indexOf(start) == 0 && !arrayContains(found, str)) found.push(str);
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

    function gatherCompletions(obj) {
      if (CodeMirror.isDir == true) {
        forEach(CodeMirror.listDir, maybeAdd);
      } else{

        if(obj == ":") {
          forEach(typesL, maybeAdd);
        }
        else {
          forEach(builtinsU, maybeAdd);
          forEach(builtinsL, maybeAdd);
          forEach(typesU, maybeAdd);
          forEach(typesL, maybeAdd);
          forEach(keywordsU, maybeAdd);
          forEach(keywordsL, maybeAdd);
          forEach(keywordsT, maybeAdd);
          forEach(keywordsD, maybeAdd);
        }
      }
    }

    if (context) {
      // If this is a property, see if it belongs to some object we can
      // find in the current environment.
      var obj = context.pop(), base;

      if (obj.className == "hive-word"){
        base = obj.string;
      }else if (obj.className == "variable"){
        base = obj.string;
      }
      else if(obj.className == "hive-type")
        base = ":" + obj.string;

      while (base != null && context.length)
        base = base[context.pop().string];
      if (base != null) gatherCompletions(base);
    }
    return found;
  }
})();