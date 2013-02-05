import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('tutorials_app.views',
                       (r'^$', 'landing'),
                       (r'^tutorials/$', 'tutorials'),
                       (r'^content/(.*)$', 'content'),
                       (r'^sync/$', 'sync_location'),
                       (r'^netinfo/$', 'network_info'),
                       (r'^file/(?P<path>.*)$', 'get_file'),
                       )

urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
                        )
