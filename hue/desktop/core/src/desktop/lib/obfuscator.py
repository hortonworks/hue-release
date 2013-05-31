import getpass
import logging
import string
import base64
from os import path
from Crypto.Cipher import AES

LOG = logging.getLogger(__name__)
HUE_MASTER_FNAME = "hue-master"

HUE_MASTER_PASSWORD = None

HARDCODED_SECRET = string.ascii_letters[:32]


class Obfuscator(object):
  passwords = {}

  def __init__(self, conf_dir):
    global HUE_MASTER_PASSWORD
    if HUE_MASTER_PASSWORD is None:
      hue_master_path = path.join(conf_dir, HUE_MASTER_FNAME)
      cryptor = AES.new(HARDCODED_SECRET, AES.MODE_CBC, 'This is an IV456')
      try:
        with open(hue_master_path, "r") as f:
          cyphertext = f.readline()
          HUE_MASTER_PASSWORD = cryptor.decrypt(cyphertext)
      except IOError:
        HUE_MASTER_PASSWORD = getpass.getpass("Enter a hue master password")
        want_to_persist = raw_input("Do you want to persist hue-master? (y/n):")
        if want_to_persist.lower() == "y":
          with open(hue_master_path) as f:
            f.write(cryptor.encrypt(HUE_MASTER_PASSWORD))
    try:
      with open(path.join(conf_dir, "hue-credentials.hks")) as f:
        for line in f:
          l = base64.decode(line)
          alias, iv, salt, cypher = l.split("::")
          decryptor = AES.new(HUE_MASTER_PASSWORD, AES.MODE_CBC, iv)
          password_with_salt = decryptor.decrypt(l)
          self.passwords[alias] = password_with_salt.replace(salt, "")
    except IOError:
      LOG.debug("Didn't found hue-credentials.hks will create new one")
      pass
