from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()
from wesharea.views import *
from emailregistration.forms import EmailAuthenticationForm

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^$', home, name='home'),
    url(r'^fb_home/$', fb_home, name='fb_home'),
    url(r'^welcome/$', welcome, name='welcome'),
    url(r'^welcomefb/$', welcomefb, name='fb-welcome'),
    (r'^accounts/', include('emailregistration.backends.registration.default_urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login', kwargs={'authentication_form':EmailAuthenticationForm}),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    (r'^facebook/', include('django_facebook.urls')), #facebook/connect
    (r'^groups/', include('groupmanager.urls')), #handling of registration delegated to groupmanager
    (r'^', include('exptracker.urls')),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )