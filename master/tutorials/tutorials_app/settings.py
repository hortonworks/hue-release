DEBUG = False
TEMPLATE_DEBUG = DEBUG

import os
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'db/lessons.db'),
    }
}

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

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djangomako.middleware.MakoMiddleware',
)

ROOT_URLCONF = 'tutorials_app.urls'

STATIC_ROOT = os.path.join(PROJECT_PATH, 'static_root')

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

STATIC_URL = "/static/"

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'staticfiles',
    'tutorials_app',
)
