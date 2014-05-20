import getpass
import logging
import string
import base64
import stat
from os import path, getenv, chmod
from desktop.lib import encryptor
from desktop.lib.paths import get_desktop_root
import hashlib
from desktop.conf import KREDENTIALS_DIR

LOG = logging.getLogger(__name__)
HUE_MASTER_FNAME = "hue-master"
HUE_CONF_DIR = config_dir = getenv("HUE_CONF_DIR", get_desktop_root("conf"))


HARDCODED_SECRET = string.ascii_letters[:32]


class Obfuscator(object):
  __HUE_MASTER_PASSWORD = None

  def set_master_password(self):
    if self.__HUE_MASTER_PASSWORD is None:
      hue_master_path = path.join(KREDENTIALS_DIR.get(), HUE_MASTER_FNAME)
      try:
        with open(hue_master_path, "r") as f:
          cyphertext = f.readline()
          self.__HUE_MASTER_PASSWORD = encryptor.DecryptWithAES(HARDCODED_SECRET, cyphertext, encryptor.STATIC_IV)
      except IOError:
        self.__HUE_MASTER_PASSWORD = getpass.getpass("Enter a hue master password:\n")
        want_to_persist = getpass.getpass("Do you want to persist hue-master? (y/n):")
        if want_to_persist.lower() == "y":
          with open(hue_master_path, "w") as f:
              f.write(encryptor.EncryptWithAES(HARDCODED_SECRET, self.__HUE_MASTER_PASSWORD, encryptor.STATIC_IV))
          chmod(hue_master_path, stat.S_IREAD|stat.S_IRGRP)


  def get_value(self, key):
    if self.__HUE_MASTER_PASSWORD is None:
        self.set_master_password()
    kredentials_path = path.join(KREDENTIALS_DIR.get(), "hue-credentials.hks")
    with open(kredentials_path, "a+") as f:
        md5 = hashlib.md5()
        md5.update(self.__HUE_MASTER_PASSWORD)
        result = None
        for line in f:
            text = base64.b64decode(line)
            alias, iv, cypher = text.split("::")
            if alias == key:
                result = encryptor.DecryptWithAES(md5.hexdigest(), cypher, iv)
        if result is None:
            password = getpass.getpass("Enter a value for %s\n" % key)
            iv = encryptor.IV()
            f.write(base64.b64encode(("%s::%s::%s" % (key, iv, encryptor.EncryptWithAES(md5.hexdigest(), password, iv)))) + "\n")
            result = password
    try:
        chmod(kredentials_path, stat.S_IREAD|stat.S_IWRITE|stat.S_IRGRP|stat.S_IWGRP)
    except Exception as ex:
      LOG.debug("Exception occurred: %s" % ex)
    return result
