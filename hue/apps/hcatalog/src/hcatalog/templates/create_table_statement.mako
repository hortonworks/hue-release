## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
## http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.
##
## |n is used throughout here, since this is not going to HTML.
##
## Reference: http://people.apache.org/~thejas/templeton_doc_latest/createtable.html
<%!
    def col_type(col):
        if col["column_type"] == "array":
            return "array <%s>" % col["array_type"]
        elif col["column_type"] == "map":
            return "map <%s, %s>" % (col["map_key_type"], col["map_value_type"])
        return col["column_type"]
%>\
<%def name="column_list(columns)">\
## Returns [{"foo": "int"}, {"bar": "string"}]-like data for columns
[\
<% first = True %>\
% for col in columns:
    % if first:
<% first = False %>\
    % else:
,\
    % endif
{"name": "`${col["column_name"]|n}`", "type": "${col_type(col)|n}"}\
% endfor
]\
</%def>\
<%!
  def escape_terminator(terminator):
    if terminator == ';':
        terminator = '\\\;'
        return terminator
    return terminator.replace('\\', '\\\\')
%>\
{
"columns": ${column_list(columns)|n},
% if table["comment"]:
"comment": "${table["comment"] | n}",
% endif
% if len(partition_columns) > 0:
"partitionedBy": ${column_list(partition_columns)|n},
% endif
## TODO: CLUSTERED BY here
## TODO: SORTED BY...INTO...BUCKETS here
##"clusteredBy": {
##"columnNames": ["id"],
##"sortedBy": [
##{ "columnName": "id", "order": "ASC" } ],
##"numberOfBuckets": 10 },
"format": {
% if table.has_key('file_format'):
    % if table.get("file_format") == "InputFormat":
"storedAs": "INPUTFORMAT \"${table["input_format_class"] | n}\" OUTPUTFORMAT \"${table["output_format_class"] | n}\"",
    % else:
"storedAs": "${table["file_format"] | n}",
    % endif
% endif
% if 'row_format' in table:
"rowFormat": {
    % if table["row_format"] == "Delimited":
        % if 'field_terminator' in table:
"fieldsTerminatedBy": "${escape_terminator(table["field_terminator"]) | n}"
        % endif
        % if 'collection_terminator' in table:
,"collectionItemsTerminatedBy": "${escape_terminator(table["collection_terminator"]) | n}"
        % endif
        % if 'map_key_terminator' in table:
,"mapKeysTerminatedBy": "${escape_terminator(table["map_key_terminator"]) | n}"
        % endif
    % else:
"serde": {
"name": "\"${table["serde_name"] | n}\""
        % if table["serde_properties"]:
        <% serde_properties = table["serde_properties"].replace("=", ":") %>\
, "properties": {
${serde_properties | n}
}
        % endif
}
    % endif
}
% endif
},
"permissions": "rwxrwxrwx",
% if table.get("use_default_location", True):
"external": "false"
% else:
"external": "true",
"location": "${table["external_location"] | n}"
% endif
}