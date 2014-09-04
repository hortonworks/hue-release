import re

NUMBER = re.compile(r'^\d*\.?\d+$')
HUMAN_NUMBER = re.compile(r'(\d*\.?\d+)\s*([KMGTkmgt])(B?)')
MULTIPLIER = dict(
    B=1,
    K=1024L,
    M=1024*1024L,
    G=1024*1024*1024L,
    T=1024*1024*1024*1024L)

def human_size(size):
  if _isinstance_of(size, [int, long, float]):
    return size
  elif isinstance(size, basestring):
    return _parse_size(size)
  else:
    raise ValueError('size=%s is not a string' % size)

def _isinstance_of(size, types=[]):
  for t in types:
    if isinstance(size, t):
      return True
  return False

def _parse_size(size):
  m = NUMBER.match(size)
  if m:
    return float(m.group(0))

  m = HUMAN_NUMBER.match(size)
  if m:
    value = float(m.group(1)) * MULTIPLIER[m.group(2).upper()]
    return value
  else:
    raise ValueError("size '%s' is not valid value" % size)
