def create_wizard(specs, curr_idx=None, done_idx=None):
  return Wizard([ Step(spec) for spec in specs ], curr_idx, done_idx)

class Step:

  def __init__(self, spec):
    self.__dict__ = self._clean_spec(spec)

  def _clean_spec(self, spec):
    assert isinstance(spec, dict)
    for attr in ["name", "title", "template"]:
      assert attr in spec
    if "skip_backward_validation" not in spec:
      spec["skip_backward_validation"] = False
    return spec

class Wizard:

  def __init__(self, steps, curr_idx, done_idx):
    """
    define a wizard. steps is an array of step specifications like
    [ { title: title, template: template } ... ]
    """
    self._steps = steps
    self.total_step_count = len(steps)
    self._curr_idx = self._validate(curr_idx) or 0
    self._done_idx = self._validate(done_idx) or 0
    if self._curr_idx > self._done_idx:
      self._curr_idx = self._done_idx

  def step(self, idx=None):
    """
    return the step specified by idx, if idx is None, return the current step 
    """
    self._validate(idx)

    if idx is None:
      idx = self._curr_idx

    return self._steps[idx]

  def step_index(self):
    return self._curr_idx

  def done_step_index(self):
    return self._done_idx

  def _validate(self, idx):
    if idx == None:
      return idx

    if idx < 0:
      raise ValueError("index must be zero or positive")

    if idx >= self.total_step_count:
      raise ValueError("index must be less than %d, but was %s" % (self.total_step_count, idx))

    return idx

  def has_more_steps(self):
    return self._done_idx < self.total_step_count - 1

  def next_step(self, target_idx=None):
    self._validate(target_idx)
    if target_idx == None:
      self._curr_idx += 1
      if self._curr_idx > self._done_idx:
        self._done_idx = self._curr_idx
    elif target_idx <= self._done_idx:
      self._curr_idx =  target_idx
    elif target_idx > self._done_idx:
      if self._done_idx == self.total_step_count - 1:
        self._curr_idx = self._done_idx
      else:
        self._done_idx += 1
        self._curr_idx = self._done_idx
