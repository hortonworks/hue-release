from django.conf.urls.defaults import *

from exapp1.views import index

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
        (r'^$', index),
)
