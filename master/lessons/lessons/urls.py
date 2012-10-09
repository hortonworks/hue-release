from django.conf.urls.defaults import *

from lessons.views import index, lesson_steps, lesson, lesson_list, content

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
        (r'^$', index),
        (r'^lesson/$', lesson_list),
		(r'^lesson/(\d+)$', lesson_steps),
		(r'^lesson/(\d+)/(\d+)$', lesson),
        (r'^content/(.*)$', content),
)
