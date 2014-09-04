from db2_export.exporter import Exporter
from db2_export.utils import db2_load_script
from db2_export.feed import feed_results
from db2_export.expect import simple_expect
from threading import Thread
import os
import codecs
import logging
LOG = logging.getLogger(__name__)

class DB2Exporter(Exporter):

  def _generate_load_script(self, options):
    return db2_load_script(options)

  def _generate_result_feed(self, generator, fifo_path, state):
    def feed_runner():
      fifo = None
      try:
          if os.path.exists(fifo_path):
              os.unlink(fifo_path)

          if not os.path.exists(fifo_path):
              os.mkfifo(fifo_path, 0700)
              fifo = codecs.open(fifo_path, mode="w", encoding="utf-8")
              feed_results(generator, fifo, state, self._limit)
      finally:
        if fifo:
          fifo.close()
          os.unlink(fifo_path)
    return Thread(target=feed_runner)

  def _generate_data_loader(self, cmd_path, out_path):
    expect = "Enter"
    password = self._req.db["password"]
    def loader_runner():
      try:
        file = open(out_path, "w")
        simple_expect(cmd_path, expect, password, file)
      finally:
        if file:
          file.close()
    return Thread(target=loader_runner)
