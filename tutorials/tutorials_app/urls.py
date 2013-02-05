import os

import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('tutorials_app.views',
                       (r'^$', 'landing'),
                       (r'^register/$', 'register'),
                       (r'^tutorials/$', 'tutorials'),
                       (r'^content/(.*)$', 'content'),
                       (r'^sync/$', 'sync_location'),
                       (r'^netinfo/$', 'network_info'),
                       )

urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': os.path.join(settings.LANDING_PATH, 'static'),
                          'show_indexes': False}),

                        (r'^file/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': os.path.join(settings.PROJECT_PATH, 'run/git_files'),
                          'show_indexes': True}),
                        )
