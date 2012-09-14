from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    '',
    url(r'execute/(?P<obj_id>\d+)/$', 'pig.views.execute', name='execute_pig'),
    url(r'(?P<obj_id>\d+)/$', 'pig.views.one_script', name='one_script'),
    url(r'$', 'pig.views.index', name='root_pig'),
)
