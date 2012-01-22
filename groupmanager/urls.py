from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from groupmanager.views import *

urlpatterns = patterns('',
    url(r'^$', list_groups, name='list_groups'), #list all groups
    url(r'^(?P<user_id>\d+)/$', list_groups, name='list_groups'), #list groups for specific user
    #TODO: url(r'^new/$', creategroup, name='create_group'), #currently via admin interface
    url(r'^(?P<group_id>\d+)/home$', group_home, name='group_home'), #home/langing page for the group
    url(r'^(?P<group_id>\d+)/update/$', update_group, name='update_group'), #update the details about the group (name desc etc)
    #TODO: url(r'^groups/(?P<group_id>\d+)/members$', listmembers, name='list_members'),
    url(r'^(?P<group_id>\d+)/members/invite_existing/$', invite_existing, name='invite_existing'), #invites existing member of the site to this group
    url(r'^(?P<group_id>\d+)/members/invite_email/$', invite_email, name='invite_email'),#invites new members via email
    url(r'^(?P<group_id>\d+)/members/invite_facebook/$', invite_facebook, name='invite_facebook'), #invites new members via facebook app request
    url(r'^members/accept_existing_invite/(?P<invite_id>\d+)/$', accept_existing_invite, name='accept_existing_invite'),
    url(r'^members/accept_email_invite/(?P<activation_key>\w+)/$', accept_email_invite, name='accept_email_invite'),
    url(r'^members/accept_facebook_invite/$', accept_facebook_invite, name='accept_facebook_invite'),
    #TODO: url(r'^(?P<group_id>\d+)/members/(?P<user_id>\d+)/$', profile, name='update_member'),
    #TODO: url(r'^(?P<group_id>\d+)/members/(?P<user_id>\d+)/remove/$', removemember, name='remove_member'),    
)

