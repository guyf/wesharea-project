import logging
from django.conf import settings
from django.contrib import messages
#from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from emailregistration.forms import EmailAuthenticationForm
from groupmanager.models import Group, Invitation

def home(request):
    if request.user.is_authenticated():
        return welcome(request)
    if request.method == 'POST':
        auth_form = EmailAuthenticationForm(request.POST)
        if auth_form.is_valid():
            user = authenticate(username=auth_form.data['username'], password=auth_form.data['password'])
            if user is not None:
                logging.debug('BBM: user %s authenticated' % user.username)
                if user.is_active:
                    login(request, user)
                    logging.debug('BBM: user %s logged in' % user.username)
                    return welcome(request)
                #else:
                    # Return a 'disabled account' error message
            else:
                messages.error(request, "Your username and/or password were not recognised, please try again.")
    else:
        auth_form = EmailAuthenticationForm()
        
    return render_to_response('home.html', {'auth_form':auth_form}, context_instance=RequestContext(request))
    

@csrf_exempt
def fb_home(request):
    logging.debug('GM: fb_home request %s' % (request))
    #assumes they have been through enhanced fb auth and granted permissions, so just connect them
    from django_facebook.connect import connect_user
    #either, login register or connect the user
    action, user = connect_user(request)
    logging.debug('GM: fb_home user returned %s  with action %s' % (user, action))

    if user:
        #TODO: could check for the request ID and check everything is legit but at the moment assume it is
        #fb_request_ids = request.GET.get('request_ids', None)
        #we have AUTO_ACCEPT set true so no need to accept the invite here just go through
        return welcome(request)

    #somthing has gone wrong authenticating them go to homepage
    return render_to_response('home.html', context_instance=RequestContext(request))


@login_required
def welcome(request):
	
    logging.debug("WSA: welcome view called with %s by %s." % (request.method, request.user.username))

    return render_to_response('welcome.html', context_instance=RequestContext(request))
