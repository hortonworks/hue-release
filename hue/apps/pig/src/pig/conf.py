# -*- coding: utf-8 -*-

from desktop.lib.conf import Config

UDF_PATH = Config(
  key="udf_path",
  help="Path where Pig udfs are stored",
  private=True,
  default="/tmp/udfs",
)
