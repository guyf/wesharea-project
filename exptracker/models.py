import logging
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.forms import ModelForm
import datetime
from decimal import *
from groupmanager.models import Group
from django_facebook.models import FacebookProfileModel


class ExptrackerProfile(models.Model):
    user = models.OneToOneField(User, related_name='exptracker_profile')
    notify_emails = models.BooleanField(default=False)
    news_emails = models.BooleanField(default=False)
    is_betatester = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username

    def create_exptracker_profile(sender, instance, created, **kwargs):
        """Create the ExpenseTrackerProfile when a new User is saved"""
        if created:
            profile = ExptrackerProfile()
            profile.user = instance
            profile.save()

    post_save.connect(create_exptracker_profile, sender=User)

class SharedExpense(models.Model):
    SHAREDEXPENSE_TYPES = (
        (u'PR', u'home you rent'),
        (u'PO', u'home you own'),
        (u'PH', u'holiday home'),
        (u'BO', u'boat'),
        (u'VS', u'summer sun holiday'),
        (u'VW', u'winter sun holiday'),
        (u'VM', u'winter sports holiday'),
        (u'VS', u'sailing holiday'),
        (u'VA', u'adventure holiday'),
        (u'VT', u'travelling or sight-seeing'),
        (u'EX', u'full-on expedition'),
        (u'VO', u'party or weekend gathering'),
        (u'BV', u'small business venture'),
        (u'BM', u'building maintenance'),
        (u'NK', u'not here (let us know what)'),
    )
    se_type = models.CharField(max_length=2, choices=SHAREDEXPENSE_TYPES, verbose_name='Type')
    se_type_other = models.CharField(max_length=150, blank=True)
    group = models.ForeignKey(Group, related_name='sharedexpense')
    name = models.CharField(max_length=150)
    currency = models.CharField(max_length=3, blank=True)
    desc = models.CharField(max_length=400, blank=True)
    start_date = models.DateField(default=datetime.date.today())
    host = models.ForeignKey(User, null=True, related_name='sharedexpense')
    notify_emails = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    get_latest_by = "start_date"
    def __unicode__(self):
        return self.name

    def total_spend(self):
        t = 0
        for ei in self.expenseitem_set.all():
            t += ei.amount
        return t

    def participant_spend(self, user):
        t = 0
        for ei in self.expenseitem_set.filter(creditor=user):
            t += ei.amount
        return t

    def per_participant_spend(self):
        p_count = self.group.participant_count() + 1 #the se will always have an organiser not returned by the participant count
        return Decimal(self.total_spend()/p_count).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    def participant_balance(self, user=None):
        #TODO: should check user not none   
        p_count = self.participant_count() + 1 #the se will always have an organiser not returned by the participant count
        if p_count == 1:
            return self.participant_spend(user)
        p_ave = Decimal(self.total_spend()/p_count).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        u_spend = self.participant_spend(user)
#        u_spend += self.participant_payments(user)
        return u_spend - p_ave

    def get_expenseitems(self, for_user=None, excl_user=None):
        if for_user is not None:
            return self.expenseitem_set.filter(creditor=for_user)
        else:
            return self.expenseitem_set.exclude(creditor=excl_user)

#    def participant_payments(self, user):
#        c = 0
#        d = 0
#        for p in self.payment_set.filter(payer=user).filter(receipt_confirmed=True):
#            c += p.amount
#        for r in self.payment_set.filter(recipient=user).filter(receipt_confirmed=True):
#            d += r.amount
#        return c - d



    def is_participant(self, user):
        return self.group.is_participant(user)
		
    def is_organiser(self, user):
        return self.group.is_organiser(user)

    def get_participants(self, excl_user=None):
        logging.debug('WSA model: participants are: %s' % self.group.get_participants(excl_user))
        return self.group.get_participants(excl_user)

    def get_organiser(self):
        return self.group.get_organiser()

    def add_participant(self, user=None):
        self.group.add_participant(user)

    def remove_expenseitems(self, user=None):
        for ei in self.expenseitem_set.filter(creditor=user):
            ei.delete()
#        for p in self.payment_set.filter(payer=user):
#            p.delete()
#        for r in self.payment_set.filter(recipient=user):
#            r.delete()

    def participant_count(self):
        return self.group.participant_count()


class ExpenseItem(models.Model):
    sharedexpense = models.ForeignKey(SharedExpense)
    creditor = models.ForeignKey(User, related_name='creditor', verbose_name='Paid by')
    name = models.CharField(max_length=150, verbose_name='Name')
    desc = models.CharField(verbose_name='Description', max_length=400, blank=True)
    paid_date = models.DateField(verbose_name='Date paid', default=datetime.date.today())
    amount = models.DecimalField(verbose_name='Amount', max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    is_budget = models.BooleanField(default=False) #True if planned but not yet spent
    is_payment = models.BooleanField(default=False) #True if recording balancing payment between participant
    is_confirmedpayment = models.BooleanField(default=False) #True balancing payment receipt has been confirmed by recipient - not yet implemented
    is_owedtohost = models.BooleanField(default=False) #True if additional option/expense selected by the creditor - not yet implemented

    class Meta:
        ordering = ('creditor', '-paid_date')
    def __unicode__(self):
        return self.name

#class Payment(models.Model):
#    sharedexpense = models.ForeignKey(SharedExpense)
#    payer = models.ForeignKey(User, related_name='payer', verbose_name='Paid by')
#    recipient = models.ForeignKey(User, related_name='recipient', verbose_name='Paid to')
#    desc = models.CharField(verbose_name='Description', max_length=400, blank=True)
#    paid_date = models.DateField(verbose_name='Date paid', default=datetime.date.today())
#    amount = models.DecimalField(verbose_name='Amount', max_digits=12, decimal_places=2)
#    currency = models.CharField(max_length=3)
#    receipt_confirmed = models.BooleanField(verbose_name='Receipt Confirmed', default=False)

#    class Meta:
#        ordering = ('-paid_date')
#    def __unicode__(self):
#        return self.desc