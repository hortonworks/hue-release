import os
import sys
import site

LOG_DIR = "/var/log/hue_httpd"
sys.path.append("/usr/lib/hue/build/env/lib/python2.6/site-packages/Django-1.2.3")

root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, root)

site.addsitedir("/usr/lib/hue/build/env/lib/python2.6/site-packages")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desktop.settings")
os.environ.setdefault('PYTHON_EGG_CACHE', '/tmp/.hue-python-eggs')
os.environ.setdefault("DESKTOP_LOGLEVEL", "WARN")
os.environ.setdefault("DESKTOP_LOG_DIR", LOG_DIR)

if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except OSError, err:
        print >> sys.stderr, 'Failed to create log directory "%s": %s' % (LOG_DIR, err)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
