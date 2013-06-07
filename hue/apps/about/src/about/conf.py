# -*- coding: utf-8 -*-

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
  default="1.3",
)
