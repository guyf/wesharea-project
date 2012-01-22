from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()
from django.views.generic.simple import direct_to_template
from exptracker.views import *


#expense tracker website URLS
urlpatterns = patterns('',
    #TODO: url(r'^sharedexpenses/$', listsharedexpenses, name='list_sharedexpenses'), #list all sharedexpenses
    url(r'^sharedexpenses/new/$', createsharedexpense, name='create_sharedexpense'),
    url(r'^sharedexpenses/(?P<sharedexpense_id>\d+)/$', viewsharedexpense, name='view_sharedexpense'),
    url(r'^sharedexpenses/(?P<sharedexpense_id>\d+)/update$', updatesharedexpense, name='update_sharedexpense'),
    url(r'^sharedexpenses/(?P<sharedexpense_id>\d+)/expenseitems/(?P<user_id>\d+)/$', updateexpenseitems, name='update_expenseitems'),
    url(r'^sharedexpenses/(?P<sharedexpense_id>\d+)/payments/(?P<user_id>\d+)/$', makepayment, name='make_payment'),
    #TO REINSTATE: url(r'^sharedexpenses/(?P<sharedexpense_id>\d+)/payments/(?P<user_id>\d+)/confirm$', confirmpayment, name='confirm_payment'),
    url(r'^sharedexpenses/(?P<sharedexpense_id>\d+)/removeparticipant/(?P<user_id>\d+)/$', wsaremoveparticipant, name='wsa_remove_participant'),
    #url(r'^sharedexpense/(?P<sharedexpense_id>\d+)/$', sharedexpense, name='sharedexpense'),
    #url(r'^editsharedexpense/(?P<sharedexpense_id>\d+)/$', editsharedexpense, name='editsharedexpense'),
    #url(r'^addexpenseitems/(?P<sharedexpense_id>\d+)/(?P<user_id>\d+)/$', addexpenseitems, name='addexpenseitems'), #view to add expenseitems from a formset
    #url(r'^makepayment/(?P<sharedexpense_id>\d+)/(?P<user_id>\d+)/$', makepayment, name='makepayment'),
)