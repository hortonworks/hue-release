import os

import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('tutorials_app.views',
                       (r'^$', 'landing'),
                       (r'^register/$', 'register'),
                       (r'^register/skip/$', 'register_skip'),
                       (r'^registration_form/$', 'registration_form_index'),
                       (r'^tutorials/$', 'tutorials'),
                       (r'^content/(.*)$', 'content'),
                       (r'^sync/$', 'sync_location'),
                       (r'^netinfo/$', 'network_info'),
                       (r'^refresh/$', 'refresh'),
                       )

urlpatterns += patterns('',
                        (r'^file/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': os.path.join(settings.PROJECT_PATH, 'run/git_files'),
                          'show_indexes': True}),

                        (r'^(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': settings.LANDING_PATH,
                          'show_indexes': False}),
                        )
