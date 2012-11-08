import settings
from django.conf.urls.defaults import *
from views import (index, lesson_steps, lesson,
                   lesson_list, content, sync_location, 
                   lesson_static)

urlpatterns = patterns('',
                       (r'^$', index),
                       (r'^lesson/$', lesson_list),
                       (r'^lesson/(\d+)$', lesson_steps),
                       (r'^lesson/(\d+)/(\d+)/$', lesson),
                       (r'^lesson/(\d+)/(\d+)/(.*)', lesson_static),
                       (r'^content/(.*)$', content),
                       (r'^sync/$', sync_location),
                       )

urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
                        )
