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

  function scriptHint(editor, keywords, getToken, kwset) {
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

      token.className="pig-word";
    }

    if (token.string.indexOf("/")> -1) {
      token.string = token.string.substring(token.string.lastIndexOf("/") + 1);
    };


    var tprop = token;
    // If it's not a 'word-style' token, ignore the token.

    if (!/^[.,\w$_-]*$/.test(token.string)) {
      token = tprop = {start: cur.ch, end: cur.ch, string: "", state: token.state,
        className: token.string == ":" ? "pig-type" : null};
    }

    if (!context) var context = [];
    context.push(tprop);

    var completionList = getCompletions(token, context, kwset);
    completionList = completionList.sort();
    //prevent autocomplete for last word, instead show dropdown with one word
    if(completionList.length == 1) {
      completionList.push(" ");
    }

    return {list: completionList,
            from: CodeMirror.Pos(cur.line, token.start),
            to: CodeMirror.Pos(cur.line, token.end)};
  }

  function toTitleCase(str) {
    return str.replace(/(?:^|\s)\w/g, function(match) {
      return match.toUpperCase();
    });
  }

  CodeMirror.registerHelper("hint", "pig", function(editor) {
    return scriptHint(editor, pigKeywordsU, function (e, cur) {return e.getTokenAt(cur);});
  });

  CodeMirror.listDir = [];
  CodeMirror.isHCat = false;
  CodeMirror.isDir = false;

  CodeMirror.kwset = {
    'keywords':[],
    'builtins':[],
    'types':[],
    'tables':[],
    'db':[]
  };

  var pigKeywords = "VOID IMPORT RETURNS DEFINE LOAD FILTER FOREACH ORDER CUBE DISTINCT COGROUP "
      + "JOIN CROSS UNION SPLIT INTO IF OTHERWISE ALL AS BY USING INNER OUTER ONSCHEMA PARALLEL "
      + "PARTITION GROUP AND OR NOT GENERATE FLATTEN ASC DESC IS STREAM THROUGH STORE MAPREDUCE "
      + "SHIP CACHE INPUT OUTPUT STDERROR STDIN STDOUT LIMIT SAMPLE LEFT RIGHT FULL EQ GT LT GTE LTE "
      + "NEQ MATCHES TRUE FALSE DESCRIBE ILLUSTRATE REGISTER EXPLAIN DUMP";
  var pigKeywordsU = pigKeywords.split(" ");
  var pigKeywordsL = pigKeywords.toLowerCase().split(" ");
  CodeMirror.kwset.keywords = CodeMirror.kwset.keywords.concat(pigKeywordsL).concat(pigKeywordsU)

  var pigTypes = "BOOLEAN INT LONG FLOAT DOUBLE CHARARRAY BYTEARRAY BAG TUPLE MAP";
  var pigTypesU = pigTypes.split(" ");
  var pigTypesL = pigTypes.toLowerCase().split(" ");
  CodeMirror.kwset.types = CodeMirror.kwset.types.concat(pigTypesL).concat(pigTypesU)

  var pigBuiltins = "ABS ACOS ARITY ASIN ATAN AVG BAGSIZE BINSTORAGE BLOOM BUILDBLOOM CBRT CEIL "
      + "CONCAT COR COS COSH COUNT COUNT_STAR COV CONSTANTSIZE CUBEDIMENSIONS DIFF DISTINCT DOUBLEABS "
      + "DOUBLEAVG DOUBLEBASE DOUBLEMAX DOUBLEMIN DOUBLEROUND DOUBLESUM EXP FLOOR FLOATABS FLOATAVG "
      + "FLOATMAX FLOATMIN FLOATROUND FLOATSUM GENERICINVOKER INDEXOF INTABS INTAVG INTMAX INTMIN "
      + "INTSUM INVOKEFORDOUBLE INVOKEFORFLOAT INVOKEFORINT INVOKEFORLONG INVOKEFORSTRING INVOKER "
      + "ISEMPTY JSONLOADER JSONMETADATA JSONSTORAGE LAST_INDEX_OF LCFIRST LOG LOG10 LOWER LONGABS "
      + "LONGAVG LONGMAX LONGMIN LONGSUM MAX MIN MAPSIZE MONITOREDUDF NONDETERMINISTIC OUTPUTSCHEMA  "
      + "PIGSTORAGE PIGSTREAMING RANDOM REGEX_EXTRACT REGEX_EXTRACT_ALL REPLACE ROUND SIN SINH SIZE "
      + "SQRT STRSPLIT SUBSTRING SUM STRINGCONCAT STRINGMAX STRINGMIN STRINGSIZE TAN TANH TOBAG "
      + "TOKENIZE TOMAP TOP TOTUPLE TRIM TEXTLOADER TUPLESIZE UCFIRST UPPER UTF8STORAGECONVERTER";
  var pigBuiltinsU = pigBuiltins.split(" ").join("() ").split(" ");
  var pigBuiltinsL = pigBuiltins.toLowerCase().split(" ").join("() ").split(" ");
  var pigBuiltinsC = ("BagSize BinStorage Bloom BuildBloom ConstantSize CubeDimensions DoubleAbs "
      + "DoubleAvg DoubleBase DoubleMax DoubleMin DoubleRound DoubleSum FloatAbs FloatAvg FloatMax "
      + "FloatMin FloatRound FloatSum GenericInvoker IntAbs IntAvg IntMax IntMin IntSum "
      + "InvokeForDouble InvokeForFloat InvokeForInt InvokeForLong InvokeForString Invoker "
      + "IsEmpty JsonLoader JsonMetadata JsonStorage LongAbs LongAvg LongMax LongMin LongSum MapSize "
      + "MonitoredUDF Nondeterministic OutputSchema PigStorage PigStreaming StringConcat StringMax "
      + "StringMin StringSize TextLoader TupleSize Utf8StorageConverter").split(" ").join("() ").split(" ");
  CodeMirror.kwset.builtins = CodeMirror.kwset.builtins.concat(pigBuiltinsL).concat(pigBuiltinsU).concat(pigBuiltinsC)

  function getCompletions(token, context, keywords_) {

    var found = [], start = token.string;
    var keywordsSet = CodeMirror.kwset;
    var keywords = (typeof keywords_ == 'string')? [keywords_] : keywords_ || [];
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
          forEach(pigTypesL, maybeAdd);
        }
        else {
          for (var i = keywords.length - 1; i >= 0; i--) {
            forEach(CodeMirror.kwset[keywords[i]], maybeAdd);
          };
        }
      }
    }
    if (keywords.length == 0) {
      for (var setname in keywordsSet) {
        keywords.push(setname);
      }
    } 

    if (context) {
      // If this is a property, see if it belongs to some object we can
      // find in the current environment.
      var obj = context.pop(), base;

      if (obj.className == "pig-word")
        base = obj.string;
      else if(obj.className == "pig-type")
        base = ":" + obj.string;
      else if(obj.className == "pig-table")
        base = obj.string;

      while (base != null && context.length)
        base = base[context.pop().string];
      if (base != null) gatherCompletions(base);
    }
    return found;
  }
})();