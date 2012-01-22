from django.conf.urls.defaults import *
from emailregistration.forms import EmailRegistrationForm


urlpatterns = patterns('',
    url(r'^register/$', 'registration.views.register', {'backend':'emailregistration.backends.registration.DefaultEmailRegBackend','form_class': EmailRegistrationForm}, name='registration_register'),
    #TODO: should implement a default view for the below - in the meantime it is in bbm
    #url(r'^invitation/(?P<user_id>\d+)/(?P<activation_key>\w+)/$', registration_invitation, name='registration_invitation'),
    (r'', include('registration.backends.default.urls')),
)