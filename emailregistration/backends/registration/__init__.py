import uuid, logging
from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User

from registration import signals
from registration.models import RegistrationProfile
from registration.backends.simple import SimpleBackend
from registration.backends.default import DefaultBackend
from emailregistration.forms import EmailRegistrationForm


class SimpleEmailRegBackend(SimpleBackend):
    """
    A registration backend which extends registration SimpleBackend
    and overwrites register to allows registration with email address 
    only (by creating a unique username) and if availble also stores first_name 
    and last_name of the new user. Also overwrites get_form_class and
    post_registration_redirect to return custom values
    
    """ 
        
    def register(self, request, logon=True, **kwargs):
        """
        Create and immediately log in a new user.
        
        """
        #create them a random user_id for the username field
        username = _create_username(kwargs['first_name'], kwargs['last_name'])
        
        #get the rest of the details from the form data passed in as args
        logging.debug('ER: SimpleEmailRegBackend kwargs %s' % str(kwargs))
        email, password, first_name, last_name = kwargs['email'], kwargs['password1'], kwargs['first_name'], kwargs['last_name']
        User.objects.create_user(username, email, password)
        # authenticate() always has to be called before login(), and
        # will return the user we just created.
        new_user = authenticate(username=username, password=password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        if logon:
            login(request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user

    def get_form_class(self, request):
        return EmailRegistrationForm

    def post_registration_redirect(self, request, user):
        """
        After registration, redirect to the user's account page.
        
        """
        return ('registration_complete', (), {})


class DefaultEmailRegBackend(DefaultBackend):
    """
    A registration backend which extends registration DefaultBackend
    and overwrites register to allows registration with email address 
    only (by creating a unique username) and if availble also stores first_name 
    and last_name of the new user. Also overwrites get_form_class and
    post_registration_redirect to return custom values
    """
    def register(self, request, **kwargs):

        #create them a random user_id for the username field
        username = _create_username(kwargs['first_name'], kwargs['last_name'])
            
        #get the rest of the details from the form data passed in as args
        logging.debug('ER: DefaultEmailRegBackend kwargs %s' % str(kwargs))
        email, password, first_name, last_name = kwargs['email'], kwargs['password1'], kwargs['first_name'], kwargs['last_name']
        
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site)
        #Deviates from standard registration from here
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        
        #Returns to standard registration after here
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)


        return new_user


    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        return EmailRegistrationForm


class InviteEmailRegBackend(DefaultBackend):
    """
    A registration backend which extends registration DefaultBackend
    and overwrites register to allow invitation of someone else by email address 
    Also overwrites get_form_class and post_registration_redirect to return custom values
    """
    def register(self, request, **kwargs):

        #get the rest of the details from the form data passed in as args
        logging.debug('ER: DefaultEmailRegBackend kwargs %s' % str(kwargs))
        email, first_name, last_name = kwargs['email'], kwargs['first_name'], kwargs['last_name']
        
        username = _create_username(first_name, last_name)
        password = uuid.uuid4().hex[:8]
        
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site, invite=True)
        #Deviates from standard registration from here
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        
        #Returns to standard registration after here
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)


        return new_user


    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        return EmailRegistrationForm

def _create_username(fname='', lname=''):
    """
    Appends first and last names together to make things readable
    then fills out the rest of the field with random characters to
    make it unique.
    """
    username = str(fname+lname+'-')
    username += uuid.uuid4().hex[:(30-len(username))]
    try:
        while True:
            User.objects.get(username=username)
            username = uuid.uuid4().hex[:(30-len(username))]
    except User.DoesNotExist:
        pass
    return username