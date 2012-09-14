from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from tastypie.api import Api
from pig import resource

v1_api = Api(api_name='v1')
for item in resource.__all__:
    v1_api.register(getattr(resource, item)())

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^accounts/login/$', 'profile.views.login', name='login_auth'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        dict(next_page='/accounts/login/'), name='logout'),
    (r'^pig/', include('pig_console.pig.urls')),
    url(r'^api/', include(v1_api.urls)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    )

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
        )
