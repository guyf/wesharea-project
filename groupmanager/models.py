import datetime, logging
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Group(models.Model):
    participant = models.ManyToManyField(User, blank=True,  null=True, related_name='participant')
    organiser = models.ForeignKey(User, related_name='organiser')
    open_organiser = models.BooleanField(default=False)
    name = models.CharField(max_length=150)
    desc_short = models.CharField(max_length=400, verbose_name='Short description (400 chars)')
    desc_long = models.TextField(blank=True, verbose_name='Long description')
    created_date = models.DateField(default=datetime.date.today)
    notify_emails = models.BooleanField(default=False)
    is_mem_get_mem = models.BooleanField(default=True)
    is_open = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def is_member(self, user): #either participant or organiser
        if self.is_organiser(user):
            return True
        elif self.is_participant(user):
            return True
        else:
            return False

    def is_participant(self, user):
        for p in self.participant.all():
            if p == user:
                return True
            else:
                continue
        return False
		
    def is_organiser(self, user):
        if self.organiser == user:
            return True
        return False

    def get_members(self): #organiser and then participants
        ms = []
        ms.append(self.organiser)
        ms.extend(self.get_participants())
        return ms
		
    def get_participants(self, excl_user=None):
        if excl_user is not None:
            ps = self.participant.filter(~Q(pk=excl_user.id))
        else:
            ps = self.participant.all()
        return list(ps)

    def get_organiser(self):
        return self.organiser

    def add_participant(self, user=None):
        self.participant.add(user)

    def remove_participant(self, user=None):
        self.participant.remove(user)

    def participant_count(self):
        return self.participant.count()

    def total_invitations(self, for_user=None):
        if for_user is not None:
            return self.invitation_set.filter(inviter=for_user).count()
        else:
            return self.invitation_set.all().count()
            
    def total_accepted(self, for_user=None):
        if for_user is not None:
            return self.invitation_set.filter(inviter=for_user).filter(accepted_datetime__isnull=False).count()
        else:
            return self.invitation_set.filter(accepted_datetime__isnull=False).count()

    def total_converted(self, for_user=None):
        if for_user is not None:
            return self.invitation_set.filter(inviter=for_user).filter(converted_datetime__isnull=False).count()
        else:
            return self.invitation_set.filter(converted_datetime__isnull=False).count()

    def get_accepted_invitations(self, for_user=None):
        if for_user is not None:
            return self.invitation_set.filter(accepted_datetime__isnull=False).filter(inviter=for_user)
        else:
            return self.invitation_set.filter(accepted_datetime__isnull=False)

    def get_issued_invitations(self, for_user=None):
        if for_user is not None:
            return self.invitation_set.filter(rejected_datetime__isnull=True).filter(accepted_datetime__isnull=True).filter(inviter=for_user)
        else:
            return self.invitation_set.filter(rejected_datetime__isnull=True).filter(accepted_datetime__isnull=True)

    def remove_invitations(self, user=None):
        if for_user is not None:
            for r in self.invitation_set.filter(inviter=user):
                r.delete()
        else:
            for r in self.invitation_set.all():
                r.delete()
        return True

class Invitation(models.Model):
    group = models.ForeignKey(Group)
    inviter = models.ForeignKey(User, related_name='inviter', verbose_name=_('Invited by'))
    invitee = models.ForeignKey(User, related_name='invitee', verbose_name=_('Invitee'))
    message = models.CharField(_('Invitation message'), max_length=400, blank=True)
    issued_datetime = models.DateTimeField(_('Date invited'), auto_now_add=True)
    accepted_datetime = models.DateTimeField(_('Date accepted'), null=True, blank=True)
    rejected_datetime = models.DateTimeField(_('Date rejected'), null=True, blank=True)
    converted_datetime = models.DateTimeField(_('Date converted'), null=True, blank=True)
    reg_activation_key = models.CharField(_('Registration activation key'), max_length=40, blank=True)
    fb_invite_id = models.CharField(_('Facebook invite id'), max_length=100, blank=True)
    fb_invite_raw_data = models.TextField(_('Facebook invite raw data'), blank=True)

    class Meta:
        ordering = ('inviter', '-issued_datetime')
        
    def __unicode__(self):
        return str('From %s to %s' % (self.inviter, self.invitee))

    def accept_invitation(self):
        if self.accepted_datetime is None: #could have been accepted automatically when sent (used by wesharea)
            logging.debug('GM: accepted invitation %s.' % self)
            self.accepted_datetime = datetime.datetime.now()
            self.save()
            #add the user to the group
            self.group.participant.add(self.invitee)
            self.group.save()
        return True

    def decline_invitation(self):
        logging.debug('GM: decline invitation %s.' % self)
        self.rejected_datetime = datetime.datetime.now()
        self.save()
        return True

    def convert_invitation(self):
        logging.debug('GM: utils converted invitation %s.' % self)
        self.converted_datetime = datetime.datetime.now()
        self.save()
        return True
