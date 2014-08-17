import os

class Exporter:

  def __init__(self, export_request, state, result, limit):
    self._req = export_request
    self._result = result
    self._limit = limit
    self._state = state

  def export(self):
    base_path = self._get_file_path(self._state)

    self._create_load_script(base_path)
    self._result.data_generator()
    reader = self._generate_result_feed(
      self._result.data_generator(), base_path + ".fifo", self._state)
    loader = self._generate_data_loader(base_path + ".sh",
        base_path + ".out")

    loader.start()
    reader.start()

    return self._state.id

  def _create_load_script(self, base_path):
    script = self._generate_load_script(
      self._load_options(base_path, self._req))
    cmd_path = base_path + ".sh"
    file = open(cmd_path, "w")
    file.write(script)
    file.close()

    os.chmod(cmd_path, 0700)

  def _load_options(self, base_path, req):
    return dict(
      db        = req.db["database"],
      user      = req.db["user"],
      password  = req.db["password"],
      fifo      = base_path + ".fifo",
      message   = base_path + ".msg",
      operation = req.operation,
      schema    = req.table["schema"],
      table     = req.table["table"] )

  def _get_file_path(self, state):
    return "/tmp/bw-export-%d" % state.id
