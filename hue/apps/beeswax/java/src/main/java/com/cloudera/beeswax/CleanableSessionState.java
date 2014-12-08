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
package com.cloudera.beeswax;

import java.io.IOException;

import org.apache.hadoop.hive.conf.HiveConf;
import org.apache.hadoop.hive.ql.history.HiveHistory;
import org.apache.hadoop.hive.ql.session.SessionState;

/**
 * Cleanable object of type SessionState.
 *
 * This lets us clean object references held by
 * {@link SessionState} (specifically {@link HiveHistory}.
 * Cleanup is needed since via RunningQueryState object we keep
 * a session alive for EVICTION_INTERVAL time period.
 * Refer HUE-326.
 *
 */
public class CleanableSessionState extends SessionState {

  
  public CleanableSessionState(HiveConf conf) {
    super(conf);
  }

  public void destroyHiveHistory() throws IOException{	
    this.hiveHist = null;
    this.close();
  }
}
