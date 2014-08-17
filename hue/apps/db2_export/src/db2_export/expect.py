import os
from subprocess import Popen, PIPE, STDOUT

def simple_expect(cmd, expect, input, stdout=None):
  """
  Open a virtual terminal, spawn a process and run the command "cmd".
  When "expect" presents, send "input". 
  Redirect stdout and stderr of the command's output.
  """
  master, slave = os.openpty()
  p = Popen(cmd, stdin=slave, stdout=PIPE, stderr=STDOUT)

  # read the process' stdout until eof or found expect
  if read_until_expect_or_eof(expect, p.stdout, stdout):
    # found
    file = os.fdopen(master, "w")
    file.write(input)
    file.write("\n")
    file.close()

  for line in p.stdout:
    stdout.write(line)

def read_until_expect_or_eof(expect, src, dest=None):
  """
  Read and record. return found or not 
  """
  idx = 0
  char = src.read(1)
  while char != "":
    if dest:
      dest.write(char)
    if char == expect[idx]:
      idx += 1
      if idx >= len(expect):
        break
    elif char == expect[0]:
      idx = 1
    else:
      idx = 0
    char = src.read(1)
  return char != ""

def record_stdout(src, dest):
  dest.close()
