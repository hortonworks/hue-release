CodeMirror.defineMode("hive", function(config) {
  var indentUnit = config.indentUnit;
  var curPunc;

  function wordRegexp(words) {
    return new RegExp("^(?:" + words.join("|") + ")$", "i");
  }
  var ops = wordRegexp(["str", "lang", "langmatches", "datatype", "bound", "sameterm", "isiri", "isuri",
                        "isblank", "isliteral", "union", "a"]);
  var keywords = wordRegexp([
    ('CREATE'),('DATABASE'),('SCHEMA'),('TABLE'),('EXTERNAL'),('IF'),('NOT'),('EXISTS'),
   ('COMMENT'),('LOCATION'),('WITH'),('DBPROPERTIES'),('DROP'),('RESTRICT'),('CASCADE'),
   ('PARTITIONED BY'),('CLUSTERED BY'),('SORTED BY'),('ASC'),('DESC'),('INTO'),('BUCKETS'),
   ('SKEWED BY'),('ON'),('ROW FORMAT'),('STORED AS'),('STORED BY'),('WITH SERDEPROPERTIES'),
   ('TBLPROPERTIES'),('LIKE'),('DELIMITED'),('FIELDS TERMINATED BY'),('BY'),
   ('COLLECTION ITEMS TERMINATED BY'),('MAP KEYS TERMINATED BY'),('LINES TERMINATED BY'),
   ('SERDE'),('SEQUENCEFILE'),('TEXTFILE'),('RCFILE'),('INPUTFORMAT'),('OUTPUTFORMAT'),('AS'),
   ('CLUSTER BY'),('SORT BY'),('IF EXISTS'),('IF NOT EXISTS'),('ALTER'),('ADD'),('PARTITION'),
   ('MSCK'),('REPAIR'),('RECOVER'),('PARTITIONS'),('RENAME TO'),('CHANGE'),('COLUMN'),('FIRST'),
   ('AFTER'),('REPLACE COLUMNS'),('SET'),('SET TBLPROPERTIES'),('SET SERDE'),('SET SERDEPROPERTIES'),
   ('SET FILEFORMAT'),('SET LOCATION'),('TOUCH'),('ARCHIVE PARTITION'),('UNARCHIVE PARTITION'),
   ('ENABLE'),('DISABLE NO_DROP'),('DISABLE OFFLINE'),('RENAME TO PARTITION'),('VIEW'),('LOAD'),
   ('INSERT'),('FROM'),('WHERE'),('TEMPORARY'),('FUNCTION'),('INDEX'),('WITH DEFERRED REBUILD'),
   ('IDXPROPERTIES'),('SHOW'),('DATABASES'),('SCHEMAS'),('TABLES'),('EXTENDED'),('FUNCTIONS'),
   ('FORMATTED'),('INDEXES'),('IN'),('COLUMNS'),('DOT'),('DESCRIBE'),('LOCK'),('TABLESAMPLE'),
   ('UNION'),('UNION ALL'),('LATERAL'),('LATERAL VIEW'),('JOIN'),('LEFT'),('RIGHT'),('FULL'),
   ('OUTER'),('SEMI'),('CROSS'),('CROSS JOIN'),('MAPJOIN'),('STREAMTABLE'),('ALL'),('DISTINCT'),
   ('DISTRIBUTE BY'),('GROUP BY'),('LIMIT'),('AND'),('OR'),('HAVING'),('LOAD DATA'),('INPATH'),
   ('SELECT'),('IMPORT'),('EXPORT'),('INPUT__FILE__NAME'),('BLOCK__OFFSET__INSIDE__FILE'),('EXPLAIN'),
   ('OVERWRITE'),('CREATE ROLE'),('DROP ROLE\GRANT ROLE'),('REVOKE ROLE'),('USER'),('GROUP'),
   ('ROLE'),('GRANT'),('SHOW ROLE GRANT')
  ]);
  var operatorChars = /[*+\-<>=&|]/;

  function tokenBase(stream, state) {
    var ch = stream.next();
    curPunc = null;
    if (ch == "$" || ch == "?") {
      stream.match(/^[\w\d]*/);
      return "variable-2";
    }
    else if (ch == "<" && !stream.match(/^[\s\u00a0=]/, false)) {
      stream.match(/^[^\s\u00a0>]*>?/);
      return "atom";
    }
    else if (ch == "\"" || ch == "'") {
      state.tokenize = tokenLiteral(ch);
      return state.tokenize(stream, state);
    }
    else if (ch == "`") {
      state.tokenize = tokenOpLiteral(ch);
      return state.tokenize(stream, state);
    }
    else if (/[{}\(\),\.;\[\]]/.test(ch)) {
      curPunc = ch;
      return null;
    }
    else if (ch == "-") {
      var ch2 = stream.next();
      if (ch2=="-") {
      	stream.skipToEnd();
      	return "comment";
      }
    }
    else if (operatorChars.test(ch)) {
      stream.eatWhile(operatorChars);
      return null;
    }
    else if (ch == ":") {
      stream.eatWhile(/[\w\d\._\-]/);
      return "atom";
    }
    else {
      stream.eatWhile(/[_\w\d]/);
      if (stream.eat(":")) {
        stream.eatWhile(/[\w\d_\-]/);
        return "atom";
      }
      var word = stream.current(), type;
      if (ops.test(word))
        return null;
      else if (keywords.test(word))
        return "keyword";
      else
        return "variable";
    }
  }

  function tokenLiteral(quote) {
    return function(stream, state) {
      var escaped = false, ch;
      while ((ch = stream.next()) != null) {
        if (ch == quote && !escaped) {
          state.tokenize = tokenBase;
          break;
        }
        escaped = !escaped && ch == "\\";
      }
      return "string";
    };
  }

  function tokenOpLiteral(quote) {
    return function(stream, state) {
      var escaped = false, ch;
      while ((ch = stream.next()) != null) {
        if (ch == quote && !escaped) {
          state.tokenize = tokenBase;
          break;
        }
        escaped = !escaped && ch == "\\";
      }
      return "variable-2";
    };
  }


  function pushContext(state, type, col) {
    state.context = {prev: state.context, indent: state.indent, col: col, type: type};
  }
  function popContext(state) {
    state.indent = state.context.indent;
    state.context = state.context.prev;
  }

  return {
    startState: function(base) {
      return {tokenize: tokenBase,
              context: null,
              indent: 0,
              col: 0};
    },

    token: function(stream, state) {
      if (stream.sol()) {
        if (state.context && state.context.align == null) state.context.align = false;
        state.indent = stream.indentation();
      }
      if (stream.eatSpace()) return null;
      var style = state.tokenize(stream, state);

      if (style != "comment" && state.context && state.context.align == null && state.context.type != "pattern") {
        state.context.align = true;
      }

      if (curPunc == "(") pushContext(state, ")", stream.column());
      else if (curPunc == "[") pushContext(state, "]", stream.column());
      else if (curPunc == "{") pushContext(state, "}", stream.column());
      else if (/[\]\}\)]/.test(curPunc)) {
        while (state.context && state.context.type == "pattern") popContext(state);
        if (state.context && curPunc == state.context.type) popContext(state);
      }
      else if (curPunc == "." && state.context && state.context.type == "pattern") popContext(state);
      else if (/atom|string|variable/.test(style) && state.context) {
        if (/[\}\]]/.test(state.context.type))
          pushContext(state, "pattern", stream.column());
        else if (state.context.type == "pattern" && !state.context.align) {
          state.context.align = true;
          state.context.col = stream.column();
        }
      }

      return style;
    },

    indent: function(state, textAfter) {
      var firstChar = textAfter && textAfter.charAt(0);
      var context = state.context;
      if (/[\]\}]/.test(firstChar))
        while (context && context.type == "pattern") context = context.prev;

      var closing = context && firstChar == context.type;
      if (!context)
        return 0;
      else if (context.type == "pattern")
        return context.col;
      else if (context.align)
        return context.col + (closing ? 0 : 1);
      else
        return context.indent + (closing ? 0 : indentUnit);
    }
  };
});

CodeMirror.defineMIME("text/x-hive", "hive");
