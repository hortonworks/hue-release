from django.conf.urls.defaults import *
from views import index, lesson_steps, lesson, lesson_list, content

urlpatterns = patterns('',
    (r'^$', index),
    (r'^lesson/$', lesson_list),
    (r'^lesson/(\d+)$', lesson_steps),
    (r'^lesson/(\d+)/(\d+)$', lesson),
    (r'^content/(.*)$', content),
)
