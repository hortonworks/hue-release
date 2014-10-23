#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.




def write_config(config, path, variables=None):
  """
  Minimal utility to write Hadoop-style configuration
  from a configuration map (config), into a new file
  called path.
  """
  f = file(path, "w")
  try:
    f.write("""<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
""")
    keys = (variables and (variables,) or (config.keys(),))[0]
    for name in keys:
      value = config[name]
      f.write("  <property>\n")
      f.write("    <name>%s</name>\n" % name)
      f.write("    <value>%s</value>\n" % value)
      f.write("  </property>\n")
    f.write("</configuration>\n")
  finally:
    f.close()

def _write_static_group_mapping(user_group_mapping, path):
  """
  Create a Java-style .properties file to contain the static user -> group
  mapping used by tests.
  """
  f = file(path, 'w')
  try:
    for user, groups in user_group_mapping.iteritems():
      f.write('%s = %s\n' % (user, ','.join(groups)))
  finally:
    f.close()
