from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django_facebook.models import FacebookProfileModel


class UserProfile(FacebookProfileModel):
    user = models.OneToOneField(User)
    timezone = models.CharField(max_length=50, default='Europe/London', blank=True)
    is_betatester = models.BooleanField(default=False)

    def __unicode__(self):
        return (self.user.first_name + ' ' + self.user.last_name)

    def create_user_profile(sender, instance, created, **kwargs):
        """Create the ReferrerProfile when a new User is saved"""
        if created:
            profile = UserProfile()
            profile.user = instance
            profile.save()

    post_save.connect(create_user_profile, sender=User)