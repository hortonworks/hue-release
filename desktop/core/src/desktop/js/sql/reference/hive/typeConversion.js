// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

export const TYPE_CONVERSION = {
  BOOLEAN: {
    BOOLEAN: true,
    TIMESTAMP: false,
    DATE: false,
    BINARY: false,
    TINYINT: false,
    SMALLINT: false,
    INT: false,
    INTEGER: false,
    BIGINT: false,
    FLOAT: false,
    DOUBLE: false,
    DECIMAL: false,
    NUMBER: false,
    STRING: false,
    CHAR: false,
    VARCHAR: false,
    T: true
  },
  TIMESTAMP: {
    BOOLEAN: false,
    TIMESTAMP: true,
    DATE: false,
    BINARY: false,
    TINYINT: false,
    SMALLINT: false,
    INT: false,
    INTEGER: false,
    BIGINT: false,
    FLOAT: false,
    DOUBLE: false,
    DECIMAL: false,
    NUMBER: false,
    STRING: false,
    CHAR: false,
    VARCHAR: false,
    T: true
  },
  DATE: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: true,
    BINARY: false,
    TINYINT: false,
    SMALLINT: false,
    INT: false,
    INTEGER: false,
    BIGINT: false,
    FLOAT: false,
    DOUBLE: false,
    DECIMAL: false,
    NUMBER: false,
    STRING: false,
    CHAR: false,
    VARCHAR: false,
    T: true
  },
  BINARY: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: false,
    BINARY: true,
    TINYINT: false,
    SMALLINT: false,
    INT: false,
    INTEGER: false,
    BIGINT: false,
    FLOAT: false,
    DOUBLE: false,
    DECIMAL: false,
    NUMBER: false,
    STRING: false,
    CHAR: false,
    VARCHAR: false,
    T: true
  },
  TINYINT: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: false,
    BINARY: false,
    TINYINT: true,
    SMALLINT: false,
    INT: false,
    INTEGER: false,
    BIGINT: false,
    FLOAT: false,
    DOUBLE: false,
    DECIMAL: false,
    NUMBER: true,
    STRING: false,
    CHAR: false,
    VARCHAR: false,
    T: true
  },
  SMALLINT: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: false,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: false,
    INTEGER: false,
    BIGINT: false,
    FLOAT: false,
    DOUBLE: false,
    DECIMAL: false,
    NUMBER: true,
    STRING: false,
    CHAR: false,
    VARCHAR: false,
    T: true
  },
  INT: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: false,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: false,
    FLOAT: false,
    DOUBLE: false,
    DECIMAL: false,
    NUMBER: true,
    STRING: false,
    CHAR: false,
    VARCHAR: false,
    T: true
  },
  BIGINT: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: false,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: true,
    FLOAT: false,
    DOUBLE: false,
    DECIMAL: false,
    NUMBER: true,
    STRING: false,
    CHAR: false,
    VARCHAR: false,
    T: true
  },
  FLOAT: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: false,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: true,
    FLOAT: true,
    DOUBLE: false,
    DECIMAL: false,
    NUMBER: true,
    STRING: false,
    CHAR: false,
    VARCHAR: false,
    T: true
  },
  DOUBLE: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: false,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: true,
    FLOAT: true,
    DOUBLE: true,
    DECIMAL: false,
    NUMBER: true,
    STRING: true,
    CHAR: true,
    VARCHAR: true,
    T: true
  },
  DECIMAL: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: false,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: true,
    FLOAT: true,
    DOUBLE: true,
    DECIMAL: true,
    NUMBER: true,
    STRING: true,
    CHAR: true,
    VARCHAR: true,
    T: true
  },
  NUMBER: {
    BOOLEAN: false,
    TIMESTAMP: false,
    DATE: false,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: true,
    FLOAT: true,
    DOUBLE: true,
    DECIMAL: true,
    NUMBER: true,
    STRING: true,
    CHAR: true,
    VARCHAR: true,
    T: true
  },
  STRING: {
    BOOLEAN: false,
    TIMESTAMP: true,
    DATE: true,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: true,
    FLOAT: true,
    DOUBLE: true,
    DECIMAL: true,
    NUMBER: true,
    STRING: true,
    CHAR: true,
    VARCHAR: true,
    T: true
  },
  CHAR: {
    BOOLEAN: false,
    TIMESTAMP: true,
    DATE: true,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: true,
    FLOAT: true,
    DOUBLE: true,
    DECIMAL: true,
    NUMBER: true,
    STRING: true,
    CHAR: true,
    VARCHAR: true,
    T: true
  },
  VARCHAR: {
    BOOLEAN: false,
    TIMESTAMP: true,
    DATE: true,
    BINARY: false,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: true,
    FLOAT: true,
    DOUBLE: true,
    DECIMAL: true,
    NUMBER: true,
    STRING: true,
    CHAR: true,
    VARCHAR: true,
    T: true
  },
  T: {
    BOOLEAN: true,
    TIMESTAMP: true,
    DATE: true,
    BINARY: true,
    TINYINT: true,
    SMALLINT: true,
    INT: true,
    INTEGER: true,
    BIGINT: true,
    FLOAT: true,
    DOUBLE: true,
    DECIMAL: true,
    NUMBER: true,
    STRING: true,
    CHAR: true,
    VARCHAR: true,
    T: true
  }
};
