import sys
import os
import string
from time import time
import subprocess

dirs = os.path.abspath(os.curdir).split(os.path.sep)
app = string.join(dirs[:-2],os.path.sep)
sys.path.append(app)
os.environ['DJANGO_SETTINGS_MODULE'] = "tutorials_app.settings"

from tutorials_app.models import VERSION

# Check DB version. If new then do syncdb again.
new_version = False
VERSION_FILE = os.path.abspath(os.path.join(os.path.abspath(os.curdir), '../db/db_version.txt'))
if not os.path.exists(VERSION_FILE):
    new_version = True
else:
    try:
        old_version = int(file(VERSION_FILE).read())
        new_version = VERSION > old_version
    except ValueError:
        new_version = True

if new_version:
    RUN = os.path.abspath(os.path.join(os.path.abspath(os.curdir), 'run.sh'))
    subprocess.call(['bash', RUN, "--migrate"], shell=False)
    print>>file(VERSION_FILE, 'w'), VERSION
