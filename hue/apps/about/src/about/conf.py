# -*- coding: utf-8 -*-

from desktop.lib.conf import Config

TUTORIALS_PATH = Config(
  key="tutorials_path",
  help="Path where tutorials are located",
  private=True,
  default="/usr/lib/sandbox-tutorials/",
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

HADOOP_VERSION = Config(
  key="hadoop_version",
  help="Version of Hadoop being used",
  private=True,
  default="1.1.2.21",
)

HCATALOG_VERSION = Config(
  key="hcatalog_version",
  help="Version of Hcatalog being used",
  private=True,
  default="0.5.0.21",
)

PIG_VERSION = Config(
  key="pig_version",
  help="Version of Pig being used",
  private=True,
  default="0.10.1.21",
)

HIVE_VERSION = Config(
  key="hive_version",
  help="Version of Hive being used",
  private=True,
  default="0.10.0.21",
)

HUE_VERSION = Config(
  key="hue_version",
  help="Version of Hue being used",
  private=True,
  default="2.2",
)
