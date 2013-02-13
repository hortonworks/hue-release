import os

import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('tutorials_app.views',
                       (r'^$', 'landing'),
                       (r'^register/$', 'register'),
                       (r'^register/skip/$', 'register_skip'),
                       (r'^tutorials/$', 'tutorials'),
                       (r'^content/(.*)$', 'content'),
                       (r'^sync/$', 'sync_location'),
                       (r'^netinfo/$', 'network_info'),
                       )

urlpatterns += patterns('',
                        (r'^file/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': os.path.join(settings.PROJECT_PATH, 'run/git_files'),
                          'show_indexes': True}),

                        (r'^(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': settings.LANDING_PATH,
                          'show_indexes': False}),
                        )
