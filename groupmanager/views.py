import hashlib, random, logging, urllib2, ast
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import password_change
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from registration.views import register
from emailregistration.forms import EmailInvitationForm, EmailInviteAcceptForm
from groupmanager.forms import GroupForm
from groupmanager.models import Group, Invitation


@login_required
def list_groups(request, user_id=None):
    """
    list groups for user_id if specified (and logged in user is_staff)
    list groups for cureently logged in user
    list all groups if logged in user is_staff
    """
    #TODO: implement the is_staff stuff
    
    try:
        og = Group.objects.filter(organiser=request.user)
    except ObjectDoesNotExist:
        og = None
    try:
        pg = Group.objects.filter(participant=request.user)
    except ObjectDoesNotExist:
        pg = None
        
    if og or pg:
        if request.method == 'POST':
            logging.warning("GM: grouphome not supporting post yet")
            messages.error(request, 'GM: grouphome not supporting post yet')
    else:
        #this is a valid user but not part of any groups, send them to project home
        HttpResponseRedirect(reverse('welcome'))

    return render_to_response("groupmanager/list_groups.html", {'org_groups': og, 'part_groups': pg}, context_instance=RequestContext(request))


@login_required
def group_home(request, group_id):
    """
    creates a home/landing page for the group tbd what this will actually display
    """
    g = get_object_or_404(Group, pk=group_id)
        
    if not g.is_member(request.user): #not a member of this group so can't continue
        logging.warning("GM: user %s not a member of group: %s" % (request.user, group_id))
        messages.error(request, 'A group with ID %s could not be found. If you think this error should not have occurred please let us know.' % str(group_id))
        return HttpResponseRedirect(reverse('home'))
        
    if request.method == 'POST':
        logging.warning("GM: group_home not supporting post yet")
        messages.error(request, 'GM: group_home not supporting post yet')
    
    is_org=False
    if  g.is_organiser(request.user):
        is_org = True
    if g.is_mem_get_mem:
        is_mgm = True

    return render_to_response("groupmanager/group_home.html", {'group': g, 'is_org': is_org, 'is_mgm': is_mgm}, context_instance=RequestContext(request))


@login_required
def update_group(request, group_id):
    """
    simple form to update group details
    """
    g = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':
        if  g_form.is_valid():
            g = g_form.save(commit=False)
            g.save()
            return grouphome(group_id)
        else:
            messages.error(request, 'Your group was not updated, see below for more information. If you think this error should not have occurred please let us know.')
    else:
        g_form = GroupForm(instance=g)

    return render_to_response("groupmanager/edit_group.html", {'group': g, 'group_form':g_form }, context_instance=RequestContext(request))


    @login_required		
    def invite_email(request, group_id):
        """
        just a wrapper for emailregiatration backend register view which is a clone of the default registration backend
        but extended to add new users into the appropriate group.
        """
        #TODO: currently supports 1 email invite at a time need to make multiple
        #TODO: capture email text in invite message in when it is editable

        g = get_object_or_404(Group, pk=group_id)

        if request.method == 'POST':
            if g.is_organiser(request.user) or (g.is_member(request.user) and g.is_mem_get_mem) or g.is_open: #check we are the organiser or the group allows others to invite
                next_url=request.POST.get('next', None) #establish where to go next from a next field in the submitted form
                logging.debug("GM: attempting to invite a new email invited member and add to group %s then redirect to %s" % (g.name,next_url))
                user_form = EmailInvitationForm(request.POST)
                #check if this person already exists as a user. If so just invite them.
                if user_form.is_valid():
                    try:
                        logging.debug("GM: testing duplicate user by email address %s" % (user_form.data['email']))
                        u = User.objects.filter(email=user_form.data['email'])
                    except ObjectDoesNotExist:
                        from registration.backends import get_backend
                        backend = get_backend('emailregistration.backends.registration.InviteEmailRegBackend') #use custom invite backend to send invitation emails
                        #create a new inactive user and send them an activation email
                        u = backend.register(request, **user_form.cleaned_data)
                        messages.info(request, 'Sucessfully invited %s at address %s to join this group.' % (user_form.data['first_name'], user_form.data['email']))
                        #get the activation key from the new inactive user registration profile to put in the invite as a reference
                        from registration.models import RegistrationProfile
                        p = RegistrationProfile.objects.get(user=u)
                        #create the invitation in the db
                        inv = Invitation.objects.create(group_id=g.id, inviter_id=request.user.id, invitee_id=u.id, reg_activation_key=p.activation_key)
                        logging.debug("RM: create invite to group %s from %s to %s" % (g.id, request.user.id, u.id))

                    else: #user already exists (by email) so create the invitation in the db no new user no activation key
                        inv = Invitation.objects.create(group_id=g.id, inviter_id=request.user.id, invitee_id=u.id, reg_activation_key='existing user invited')
                        messages.info(request, '%s at address %s is already a user of %s and will receive an invitation to joint this group.' % (u.first_name, u.email, settings.SITE_NAME))
                        logging.debug("RM: create invite to group %s from %s to %s" % (g.id, request.user.id, u.id))
                        #TODO: notify them of the new invite by email

                else: #invalid form re-render the template, show form errors
                    logging.debug("GM: Failed to add new email invite user to group %s because posted form was invalid." % (g.name))
                    return render_to_response("groupmanager/invite_email_form.html",{'group_id': group_id, 'form':user_form },context_instance=RequestContext(request))

                if settings.AUTO_ACCEPT:  #automatically accept the invite (ie. don't wait for the invitee to do so)
                    inv.accept_invitation()

            else: #user doesn't have permission to invite into the group
                logging.error("GM: invite_email_member received request to invite users from user without correct permissions.")
                messages.error(request, 'You do not have permission to invite users to that group. If this problem persists please let us know.')

        else: #its a GET so just render the template
            user_form = EmailInvitationForm()
            return render_to_response("groupmanager/invite_email_form.html",{'group_id': group_id, 'form':user_form },context_instance=RequestContext(request))

        if next_url:
            return HttpResponseRedirect(next_url)
        return HttpResponseRedirect(reverse('group_home', args=[g.id]))


def accept_email_invite(request, activation_key):
    inv = get_object_or_404 (Invitation, reg_activation_key=activation_key)
    logging.debug("BBM: accept_email_invite view found invite %s." % str(inv))
    
    if request.method == 'POST':
        pw_form = EmailInviteAcceptForm(request.POST)
        if pw_form.is_valid():
            from registration.backends import get_backend
            reg_backend = get_backend(settings.REGISTRATION_BACKEND)
            u = reg_backend.activate(request, activation_key)
            if not u:
                logging.debug('BBM was unable to activate user with activation key %s' % (activation_key))
                messages.error(request, 'Sorry we were unable to activate your user, please try again and contact us if the problem persists')
                return HttpResponseRedirect(reverse('home'))
            else:
                logging.debug('BBM attempting to set password to %s for user %s' % (pw_form.data['password1'], u.username))
                u.set_password(pw_form.data['password1'])
                u.save()
                #authenticate the user and log them in
                auth_user = authenticate(username=u.email, password=pw_form.data['password1'])
                if auth_user is not None:
                    logging.debug('BBM: new invited user %s authenticated' % auth_user.username)
                    #accept invite
                    inv.accept_invitation()
                    login(request, auth_user)
                    messages.info(request, "Thank you %s, your account has been activated and invitation accepted" % auth_user.first_name)
                    return HttpResponseRedirect(reverse('welcome'))
                else:
                    messages.error(request, "Your username and/or password were not recognised, please try again.")
    else:
        pw_form=EmailInviteAcceptForm()
        
    return render_to_response('groupmanager/accept_email_invite.html', {'invite': inv, 'pw_form': pw_form}, context_instance=RequestContext(request))


@login_required
@csrf_exempt
def invite_facebook(request, group_id):

    g = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':
        if g.is_organiser(request.user) or (g.is_member(request.user) and g.is_mem_get_mem) or g.is_open: #check we are the organiser or the group allows others to invite
            success_url=request.GET.get('success_url', '')
            logging.debug("GM: invite_fb_members success_url: %s" % (success_url))
            user_app_requests = request.POST.getlist('user_app_requests[]')
            logging.debug("GM: looking for friends from facebook invites %s to add to group %s" % (str(user_app_requests), group_id))

            if user_app_requests:
                #TODO: should probably do this via the django_facebook api
                access_token_url = str('https://graph.facebook.com/oauth/access_token?client_id='+ settings.FACEBOOK_APP_ID + 
                                '&client_secret='+ settings.FACEBOOK_APP_SECRET + '&grant_type=client_credentials')
                logging.debug("GM: access_token_url: %s" % str(access_token_url))
                access_token = urllib2.urlopen(access_token_url).read()
                logging.debug("GM: access_token retrieved: %s" % str(access_token))
                newFbUsers = []
                for user_app_request in user_app_requests:
                    #get the whole invite and convert to a dictionary
                    #TODO: should do this via the SDK
                    invite = ast.literal_eval(urllib2.urlopen('https://graph.facebook.com/' + user_app_request + '?' + access_token).read())
                    fbid = str(invite['to']['id'])
                    logging.debug("RM: found facebook id %s from request invite %s" % (fbid, invite))
                    
                    #if they are not already a user create a new inactive user
                    try: u = User.objects.get(userprofile__facebook_id=fbid)
                    except ObjectDoesNotExist:
                        #get their public facebook profile
                        #TODO: should do this via the SDK
                        fbprofile = ast.literal_eval(urllib2.urlopen('https://graph.facebook.com/' + fbid).read())
                        
                        #add a couple of bits into the fbprofile to get it to register
                        fbprofile['password1'] = hashlib.sha1(str(random.random())).hexdigest()[:8]
                        fbprofile['email'] = ''
                        logging.debug("RM: user does not exist so adding: %s" % (str(fbprofile)))
                        
                        #find the registration backend and use it to create the new user
                        #TODO: after register set them to inactive users
                        from registration.backends import get_backend
                        backend = get_backend('emailregistration.backends.registration.SimpleEmailRegBackend') #use simple backend to create user no activation email
                        logging.debug("GM: backend: %s" % (dir(backend)))
                        u = backend.register(request, logon=False, **fbprofile)
                        
                        #take what little we can from the public fb profile and put it into the user profile
                        #TODO: could probably do this through django_facebook update_user
                        p = u.get_profile()
                        if 'id' in fbprofile:
                            p.facebook_id = fbprofile['id']
                        if 'name' in fbprofile:
                            p.facebook_name = fbprofile['name']
                        if 'link' in fbprofile:
                            p.facebook_profile_url = fbprofile['link']
                        p.raw_data = fbprofile
                        p.save()
                        
                        #create invite in db
                        inv = Invitation.objects.create(group_id=g.id, inviter_id=request.user.id, invitee_id=u.id, fb_invite_id=user_app_request, fb_invite_raw_data=invite)
                        logging.debug("RM: create invite to group %s from %s to %s via fb app request %s" % (g.id, request.user.id, u.id, user_app_request))
                    
                    else: #user already exists (by facebook ID) so just create the invitation
                        #TODO: check they are not already a member or already invited to join
                        inv = Invitation.objects.create(group_id=g.id, inviter_id=request.user.id, invitee_id=u.id, fb_invite_id=user_app_request, fb_invite_raw_data=invite)
                        messages.info(request, '%s is already a user of %s and will receive an invitation to joint this group.' % (u.first_name, settings.SITE_NAME))
                        logging.debug("RM: create invite to group %s from %s to %s" % (g.id, request.user.id, u.id))
                        #TODO: notify them of the new invite by email
                    
                    if settings.AUTO_ACCEPT:  #automatically accept the invite (ie. don't wait for the invitee to do so)
                        inv.accept_invitation()
                                          
            else:
                logging.warning("GM: addfbmembers received no user_app_requests from facebook to add users from.")
                messages.warning(request, 'We were unable to retreive the users from facebook you invited to join this group. There could be an issue connecting with facebook at the moment, please try again. If this problem persists please let us know.')

        else: #user doesn't have permission to invite into the group
            logging.error("GM: invite_fb_members received request to invite users from user without correct permissions.")
            messages.error(request, 'You do not have permission to invite users to that group. If this problem persists please let us know.')
    
    #TODO: handle get
    #else:

    if success_url:
        return HttpResponseRedirect(success_url)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@csrf_exempt
def accept_facebook_invite(request, fb_request_ids):
    
    #find the invitation and accept it
    fb_invite_id = str(fb_request_ids + '_' + str(request.user.get_profile().facebook_id))
    fbi = Invitation.objects.get(fb_invite_id=fb_invite_id)
    fbi.accept_invitation()
    #TODO: delete the app request from facebook

    messages.info(request, "Thank you %s, your account has been activated and invitation accepted" % request.user.first_name)
    return HttpResponseRedirect(reverse('welcome'))


@login_required
@csrf_exempt
def invite_existing(request, group_id):
    """
    creates a list of all contacts to whom the user has previously sent an invitation display a checkbox by each for their selection
    creates a new invitation entry for them
    """

    #TODO: allow a message to be created
    #TODO: email the invitee a notification

    g = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        if g.is_organiser(request.user) or (g.is_member(request.user) and g.is_mem_get_mem) or g.is_open: #check we are the organiser or the group allows others to invite
            next_url=request.POST.get('next', None) #establish where to go next from a next field in the submitted form
            userIDs = request.POST.getlist('user_ids[]')
            logging.debug("GM: invite_existing passed user IDs %s and asked to redirect to %s" % (userIDs,next_url))
            if userIDs:
                for userID in userIDs:
                    try:
                        u = User.objects.get(pk=userID)
                    except ObjectDoesNotExist:
                        logging.info("GM: addmembers couldn't find user with ID: %s" % (userID))
                    #create the invitation in the db
                    logging.debug("RM: create invite to group %s from %s to exsiting member %s" % (g.id, request.user.id, u.id))
                    inv = Invitation.objects.create(group_id=g.id, inviter_id=request.user.id, invitee_id=u.id)
                    #TODO: email notification
                    #send_mail(str('You have been invited to join %s:' % g.name),
                    #          str('%s %s is organising \'%s\' and is using We Share A to track all the associated expenses. Please login and input anything you spend to help %s out.' % (request.user.first_name, request.user.last_name, se.name, request.user.first_name)), 
                    #          'noreply@wesharea.com', [u.email], fail_silently=True)
                
                    if settings.AUTO_ACCEPT: #automatically accept the invite (ie. don't wait for the invitee to do so)
                        inv.accept_invitation()

            else:
                logging.warning("GM: addmembers received no user IDs to add users from.")
                messages.error(request, 'No valid users were provided to add to the group. If you think this error should not have occurred please let us know.')
                
        else: #user doesn't have permission to invite into the group
            logging.error("GM: invite_existing received request to invite users from user without correct permissions.")
            messages.error(request, 'You do not have permission to invite users to that group. If this problem persists please let us know.')
            
    else: #GET find all the users this user has previously invited and pass to template
        #TODO: rethink if this could be wider maybe controlled by user profile/privacy settings
        contacts = []
        invs = Invitation.objects.filter(inviter=request.user) #get all the invites this user has sent ever
        for inv in invs:
            #TODO: don't add them to array if they have an outstanding invite to join the group (maybe add resend option?)
            if not g.is_member(inv.invitee) and contacts.count(inv.invitee) == 0: #only if not a member and not in the array already
                contacts.append(inv.invitee)
        logging.debug("GM: addparicipants found contacts:" + str(contacts))
        invite_email_form = EmailInvitationForm()
        return render_to_response("groupmanager/invite_existing_form.html",{'group_id': g.id, 'contacts':contacts, 'form':invite_email_form },context_instance=RequestContext(request))

    
    #at the moment this view is only called by ajax post, so return where js should redirect to 
    if next_url:
        return HttpResponse(next_url)
    return HttpResponse(reverse('group_home', args=[g.id]))



def accept_existing_invite(request, invite_id):
    #TODO: allow invites sent via facebook to be accepted directly in BBM and delete from facebook
    inv = get_object_or_404(Invitation, pk=invite_id)
    
    if request.method == 'POST':
        if 'accept' in request.POST:
            inv.accept_invitation()
            messages.info(request, 'You have successfully joined %s' % inv.group.name)
        if 'decline' in request.POST:
            inv.decline_invitation()
            messages.info(request, 'You have declined the invitation to join %s' % inv.group.name)

    return HttpResponseRedirect(request.META['HTTP_REFERER'])
    

@login_required	
def profile(request, user_id=None):
	
    u = get_object_or_404(User, pk=request.user.id)
    if u == request.user:
        if request.method == 'POST':
            messages.success(request, 'Your password was successfully updated')
            return password_change(request, post_change_redirect=reverse('web-welcome'))
        else:
            return password_change(request, post_change_redirect=reverse('web-welcome'))
    else:
        messages.error(request, 'Sorry you do not have permission to see that user\'s profile, if you think you should please let us know.')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
