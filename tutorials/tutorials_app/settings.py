DEBUG = False
TEMPLATE_DEBUG = DEBUG

import os
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

REQUIRE_REGISTRATION = True

TUTORIALS_APP_PATH = '/usr/lib/tutorials'

LANDING_PATH = os.path.join(TUTORIALS_APP_PATH, 'sandbox-tutorials')

USERINFO_FILE_PATH = os.path.join(TUTORIALS_APP_PATH, 'user_info.dat')

START_SCRIPTS = os.path.join('/usr/lib/hue/tools', 'start_scripts')

HUE_VAR_PATH = os.path.join('/var/lib', 'hue')

ADMINS = ()

MANAGERS = ADMINS

USE_X_FORWARDED_HOST = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'db/lessons.db'),
    },
    'auth_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(HUE_VAR_PATH, 'desktop.db'),
    }
}

# from socket import gethostname,gethostbyname
CONTENT_FRAME_URL = lambda: "http://%s:8000/"  # % gethostbyname(gethostname()) # HUE URL param

DATABASE_ROUTERS = ['tutorials_app.db_routers.AuthRouter']

SESSION_ENGINE = 'tutorials_app.sessions_backend'

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

SITE_ID = 2
USE_I18N = False
USE_L10N = False

MEDIA_ROOT = ''
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'

SECRET_KEY = '@cn3!h2wv+1&5p=r=2f2i^qkg*(4na_z0xryv0c@1m7tv#(v)5'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
"django.core.context_processors.static",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'tutorials_app.readonly_sessions_middleware.SessionMiddleware',
    'tutorials_app.auth_middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djangomako.middleware.MakoMiddleware',
)

ROOT_URLCONF = 'tutorials_app.urls'

STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

# STATICFILES_DIRS = (
#     os.path.join(PROJECT_PATH, 'static'),
# )

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATIC_URL = "/static/"

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
    TUTORIALS_APP_PATH,
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tutorials_app',
    'gunicorn',
)

try:
    from local_settings import *
except ImportError:
    pass
