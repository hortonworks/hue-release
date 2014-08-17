from django.utils.encoding import force_unicode
import re

def human_size(num):
  return _convert(num, 1024.0, ['B','KB','MB','GB','TB'])

def human_number(num):
  return _convert(num, 1000.0, ['','K','M','G','T'])

def human_time(num):
  hours, num = divmod(num, 3600000)
  minutes, num = divmod(num, 60000)
  seconds = float(num) / 1000
  return "%i:%02i:%06.3f" % (hours, minutes, seconds)
  
def _convert(num, div, units):
  if num is None:
    return None

  format = "%d%s"
  for x in units:
    if num < div:
      return format % (round(num,1), x)
    num /= div
    format = "%.1f%s"

def intcomma(value):
  """
  Converts an integer to a string containing commas every three digits.
  For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
  """
  orig = force_unicode(value)
  new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
  if orig == new:
    return new
  else:
    return intcomma(new)
