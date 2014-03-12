# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Configuration for the about application"""

from desktop.lib.conf import Config

TUTORIALS_PATH = Config(
  key="tutorials_path",
  help="Path where tutorials are located",
  private=True,
  default="/usr/lib/tutorials/sandbox-tutorials/",
)

TUTORIALS_UPDATE_SCRIPT = Config(
  key="tutorials_update_script",
  help="Path where tutorials update script is located",
  private=True,
  default="/usr/lib/tutorials/tutorials_app/run/run.sh",
)

TUTORIALS_INSTALLED = Config(
  key="tutorials_installed",
  help="Whether tutorials installed on server",
  private=True,
  default=True,
  type=bool,
)

SANDBOX_VERSION = Config(
  key="sandbox_version",
  help="Version of Sandbox being used",
  private=True,
  default="2.1",
)

SANDBOX = Config(
  key="sandbox",
  help="Is About application installed in Sandbox",
  default=False,
  type=bool,
)

ABOUT_PAGE_TITLE = Config(
  key="about_page_title",
  help="Title on about page",
  default="Hue",
)

ABOUT_TITLE = Config(
  key="about_title",
  help="Title on about page",
  default="Hue",
)
