import logging
from django.contrib import messages
from django import template
from django.core.urlresolvers import reverse
from groupmanager.models import Group, Invitation
from django.contrib.auth.models import User

register = template.Library()

@register.simple_tag
def fullname_from_userid(user_id):
    u = User.objects.get(pk=user_id)
    return '<span class="uname">%s %s</span>' % (u.first_name, u.last_name)


@register.simple_tag
def firstname_from_userid(user_id):
    u = User.objects.get(pk=user_id)
    return u.first_name
    

@register.inclusion_tag('groupmanager/fb_invite.js')
def facebook_invite_js(group, user_firstname):
    if isinstance(group,Group):
        g = group
    else:
        g = Group.objects.get(pk=group)

    return {'user_firstname':user_firstname, 'group': g}


@register.inclusion_tag('groupmanager/show_string.html')
def facebook_photo(user):
    if isinstance(user,User):
        u = user
    else:
        u = User.objects.get(username=user)

    if u.get_profile().facebook_id is '':
        return {'string':u'<img class= "fbpic" src="/static/images/silouette.gif" alt="%s"/>' % (u.first_name)}
        
    return {'string':u'<img class="fbpic" src="https://graph.facebook.com/%s/picture" alt="%s"/>' % (u.get_profile().facebook_id, u.first_name)}


@register.simple_tag
def account_logout(user):
	
    lo = reverse('logout')
    pro = reverse('auth_password_change') #should go to profile page to update all details

    if isinstance(user,User):
        u = user
    else:
        u = User.objects.get(username=user)

    try:
        p = user.get_profile().facebook_id
    except ObjectDoesNotExist:
        logging.debug("WSA: not a facebook user so standard logout %s" % (u.username))
        return '<span class="logout">Welcome <a href="%s">%s</a>&nbsp;<a href="%s">logout</a></span>' % (pro,u.first_name,lo)

    return '<span class="logout">Welcome <a href="%s">%s</a>&nbsp;<a href="%s" onclick="F.logout(function(response){})return false;">logout</a></span>' % (pro,u.first_name,lo)

    
    
@register.inclusion_tag('groupmanager/show_string.html')
def group_invitation_summary(invitation):
    if isinstance(invitation,Invitation):
        i = invitation
    else:
        i = Invitation.objects.get(pk=invitation)
    
    logging.debug('GM: showing group invite: %s' % i)
        
    if i.accepted_datetime is None:
        return {'string':u'<span>%s %s invited %s %s to join on %s</span>' % (i.inviter.first_name, i.inviter.last_name, i.invitee.first_name, i.invitee.last_name, i.issued_datetime)}
        
    return {'string':u'<span>%s %s invited %s %s who joined on %s</span>' % (i.inviter.first_name, i.inviter.last_name, i.invitee.first_name, i.invitee.last_name, i.accepted_datetime)}


@register.inclusion_tag('groupmanager/show_string.html')
def user_invitation_summary(invitation):
    if isinstance(invitation,Invitation):
        i = invitation
    else:
        i = Invitation.objects.get(pk=invitation)
    logging.debug('GM: still showing user invite: %s' % i)

    return {'string':u'<span>%s %s has invited you to join group %s</span>' % (i.inviter.first_name, i.inviter.last_name, i.group.name)}
