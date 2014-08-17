from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('db2_export.views',
    url(r'^results/(?P<id>\d+)$', 'export_results', name='export_results'),
    url(r'^state/(?P<id>\d+)$', 'export_state', name='export_state'),
    url(r'^output/(?P<state_id>\d+)$', 'export_output', name='export_output'),
    url(r'^data/(?P<id>\d+)$', 'export_data', name='export_data'),
)
