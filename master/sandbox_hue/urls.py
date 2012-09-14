from django.conf.urls.defaults import *
from django.contrib import admin
from auth.views import *
from auth.forms import RegistrationFormProfile
from auth.signals import *

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', start_page),
	url(r'^login/$', login),
	url(r'^registration/$', registration),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/register/$', 'registration.views.register', 
		{'backend': 'registration.backends.default.DefaultBackend', 'form_class' : RegistrationFormProfile,},
		name='registration_register'),
	url(r'^accounts/', include('registration.backends.default.urls')),
	url(r'^accounts/activate/complete/$', 'auth.views.redirect_after_activation'),
)
