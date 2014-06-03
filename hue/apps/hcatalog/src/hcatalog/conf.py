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
"""Configuration for the hcatalog application"""


from desktop.lib.conf import Config

TEMPLETON_URL = Config(
    key="templeton_url",
    help="URL of Templeton(WebHcat) server",
    default="http://localhost:50111/templeton/v1/",
    private=False
)

SECURITY_ENABLED = Config(
    key="security_enabled",
    help="Whether to use kerberos auth",
    default=False,
    type=bool,
    private=False
)


def config_validator(user):
    """
    config_validator() -> [ (config_variable, error_message) ]

    Called by core check_config() view.
    """
    from pig.templeton import Templeton

    t = Templeton()
    try:
        t.get("status")
    except Exception, error:
        return [(TEMPLETON_URL, "%s" % (error.message))]
    else:
        return []

