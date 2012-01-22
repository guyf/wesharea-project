import logging
from django.contrib import messages
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from exptracker.models import SharedExpense, ExpenseItem #, Payment
from exptracker.forms import ExpenseItemForm, ExpenseItemFormSet, SharedExpenseForm #,MakePaymentForm
#from groupmanager.forms import UserForm
from django.db.models import Q

register = template.Library()



@register.inclusion_tag('exptracker/tag_view_participant.html')
def show_participant(participant, sharedexpense, user):
    if isinstance(sharedexpense,SharedExpense):
        se = sharedexpense
    else:
        se = SharedExpense.objects.get(pk=sharedexpense)

    if isinstance(user,User):
        u = user
    else:
        u = User.objects.get(username=user)

    is_org = se.is_organiser(u)
    is_me = False
    if participant.id == u.id:
        is_me = True

    expensepayment_form = ExpenseItemForm()
#    makepayment_form = MakePaymentForm()
#    confirmpayments = Payment.objects.all().filter(sharedexpense=se).filter(recipient=user).filter(receipt_confirmed=False)

#    return {'participants':participants,'sharedexpense':se,'makepayment_form':makepayment_form,'confirmpayments':confirmpayments,'chn':chn}
    return {'participant':participant,'sharedexpense':se, 'expensepayment_form':expensepayment_form, 'is_org':is_org, 'is_me': is_me}


@register.inclusion_tag('exptracker/tag_view_expenseitems.html')
def view_expenseitems(sharedexpense, for_user=None):
	#TODO: validate there are legitimate paramters
    if isinstance(sharedexpense,SharedExpense):
        se = sharedexpense
    else:
        se = SharedExpense.objects.get(pk=sharedexpense)

    if for_user is not None:
        if isinstance(for_user,User):
            u = for_user
        else:
            u = User.objects.get(username=for_user)
        expenseitems = se.get_expenseitems(for_user=u)
    else:
        expenseitems = se.get_expenseitems()

    ei_dict = []
    for ei in expenseitems:
        tmp_dict=model_to_dict(ei)
        #remove unwanted fields
        tmp_dict.pop('creditor')
        tmp_dict.pop('sharedexpense')
        tmp_dict.pop('id')
        ei_dict.append(tmp_dict)

    logging.debug("WSA: ExpenseItem dict list for view_expenseitems %s" % (ei_dict))
    return { 'ei_dict': ei_dict, 'sharedexpense': se}


@register.inclusion_tag('exptracker/tag_edit_expenseitems.html')
def edit_expenseitems(sharedexpense, for_user=None):
    #TODO: validate there are legitimate paramters
    if isinstance(sharedexpense,SharedExpense):
        se = sharedexpense
    else:
        se = SharedExpense.objects.get(pk=sharedexpense)

    if for_user != None:
        if isinstance(for_user,User):
            u = for_user
        else:
            u = User.objects.get(username=for_user)

        #create an array of formset with just one in it
        expenseitem_formsets = []
        expenseitem_formset = ExpenseItemFormSet(queryset=ExpenseItem.objects.all().filter(sharedexpense=se).filter(creditor=u), prefix=u.id)
        expenseitem_formsets.append(expenseitem_formset)
    
    else:
        o = se.get_organiser()
        expenseitem_formsets = []
        expenseitem_formset = ExpenseItemFormSet(queryset=ExpenseItem.objects.all().filter(sharedexpense=se).filter(creditor=o), prefix=o.id)
        expenseitem_formsets.append(expenseitem_formset)
        #then append formsets for participants
        for p in se.get_participants():	
            expenseitem_formset = ExpenseItemFormSet(queryset=ExpenseItem.objects.all().filter(sharedexpense=se).filter(creditor=p), prefix=p.id)
            expenseitem_formsets.append(expenseitem_formset)

    return {'sharedexpense':se, 'expenseitem_formsets':expenseitem_formsets}


@register.inclusion_tag('exptracker/tag_balances_widget.html')
def balances_widget(sharedexpense, participants):
    if isinstance(sharedexpense,SharedExpense):
        se = sharedexpense
    else:
        se = SharedExpense.objects.get(pk=sharedexpense)

    return {'sharedexpense':se, 'participants':participants}


@register.inclusion_tag('exptracker/tag_sharedexpense_menu.html')
def sharedexpense_menu(user):
    if isinstance(user,User):
        u = user
    else:
        u = User.objects.get(pk=user)

    ses = []

    for se in SharedExpense.objects.all():
        if se.is_participant(u) or se.is_organiser(u):
            ses.append(se)

    return {'sharedexpenses':ses}



@register.inclusion_tag('exptracker/tag_sharedexpense_list.html')
def sharedexpense_list(user):
    if isinstance(user,User):
        u = user
    else:
        u = User.objects.get(pk=user)

    ses = []

    for se in SharedExpense.objects.all():
        if se.is_participant(u) or se.is_organiser(u):
            ses.append(se)

    return {'sharedexpenses':ses}


@register.simple_tag
def show_sharedexpense_total(sharedexpense, user=None):
    if isinstance(sharedexpense,SharedExpense):
        se = sharedexpense
    else:
        se = SharedExpense.objects.get(pk=sharedexpense)

    if user is None:
        return '<span class="currency total">%s</span>' % ('{0:.2f}'.format(se.total_spend()))
    else:
        if isinstance(user,User):
            u = user
        else:
            u = User.objects.get(username=user)
	
	return '<span class="currency total">%s</span>' % ('{0:.2f}'.format(se.participant_spend(u)))
	
	
@register.simple_tag
def show_user_balance(sharedexpense, user):	
    if isinstance(sharedexpense,SharedExpense):
        se = sharedexpense
    else:
        se = SharedExpense.objects.get(pk=sharedexpense)

    if isinstance(user,User):
        u = user
    else:
        u = User.objects.get(username=user)

    return '<div class="currency total">%s</div>' % ('{0:.2f}'.format(se.participant_balance(user=u)))


@register.simple_tag
def show_per_participant_spend(sharedexpense):	
    if isinstance(sharedexpense,SharedExpense):
        se = sharedexpense
    else:
        se = SharedExpense.objects.get(pk=sharedexpense)

    return '<span class="currency total">%s</span>' % ('{0:.2f}'.format(se.per_participant_spend()))

@register.simple_tag
def show_fullname_from_userid(user_id):
    u = User.objects.get(pk=user_id)
    return '<span class="uname">%s %s</span>' % (u.first_name, u.last_name)

@register.simple_tag
def show_firstname_from_userid(user_id):
    u = User.objects.get(pk=user_id)
    return u.first_name


def __get_facebook_profiles(sharedexpense, excl_username=None, for_username=None):
	#TODO: check a valid combination of parameters
	#Assemble a Facebook profiles of the participants in this sharedexpense or if username supplied just for that user	
    if isinstance(sharedexpense,SharedExpense):
        se = sharedexpense
    else:
        se = SharedExpense.objects.get(pk=sharedexpense)

    friends_ids = []
    if for_username is None:
        if se.get_organiser().username != excl_username:
	        friends_ids.append(se.get_organiser().username)
        for participant in se.get_participants():
            if participant.username != excl_username:
                friends_ids.append(participant.username)
    else:
        friends_ids.append(for_username)

    profiles = se.get_organiser().facebook_profile.get_friends_profiles(friends_ids=friends_ids)
    logging.debug("WSA: sharedexpense participants facebook profiles:" + str(profiles))
    return profiles



#TAGS UNUSED AT PRESENT

#currently using the fb request dialogue to select friends whether they are already in we share db or not so tag not needed can be found in projects.snippets.py
#@register.inclusion_tag('exptracker/tag_select_participant.html')
#def select_participants(sharedexpense):

#Now replicated in view
#@register.inclusion_tag('exptracker/tag_select_nonlink_participants.html')
#def select_nonlink_participants(sharedexpense):

#@register.inclusion_tag('exptracker/tag_edit_nonlink_participant.html')
#def edit_nonlink_participant(sharedexpense, user=None):
	
#    if isinstance(sharedexpense,SharedExpense):
#        se = sharedexpense
#    else:
#        se = SharedExpense.objects.get(pk=sharedexpense)

#    if user is not None:
#        if isinstance(user,User):
#            u = user
#        else:
#            u = User.objects.get(username=user)
#        user_form = UserForm(instance=u)
#        update = True
#    else:
#        user_form = UserForm()
#        update = False

#    return {'sharedexpense': se, 'user_form':user_form }

#@register.inclusion_tag('exptracker/tag_menu_tile.html')
#def show_large_menu_tile(sharedexpense, chn):
#    if isinstance(sharedexpense,SharedExpense):
#        se = sharedexpense
#    else:
#        se = SharedExpense.objects.get(pk=sharedexpense)

#    return {'sharedexpense':se,'class':'tilelarge','chn':chn}


#@register.inclusion_tag('exptracker/tag_menu_tile.html')
#def show_small_menu_tile(sharedexpense, chn):
#    if isinstance(sharedexpense,SharedExpense):
#        se = sharedexpense
#    else:
#        se = SharedExpense.objects.get(pk=sharedexpense)

#    return {'sharedexpense':se,'class':'tilesmall','chn':chn}


#@register.inclusion_tag('exptracker/tag_stack_graph.html')
#def show_expenditure_stack_graph(sharedexpense):
#    if isinstance(sharedexpense,SharedExpense):
#        se = sharedexpense
#    else:
#        se = SharedExpense.objects.get(pk=sharedexpense)	
	
#    data = []
#    tmp = []
#    tmp.append(str(se.participant_spend(se.organiser)))
#    tmp.append(str(se.organiser.first_name))
#    data.append(tmp)

#    for p in se.participants.all():
#        tmp = []
#        tmp.append(str(se.participant_spend(p)))
#        tmp.append(str(p.first_name))
#        data.append(tmp)

#    logging.debug("WSA: Chart data: %s" % str(data))	
#    return {'data':data, 'currency': se.currency}


#@register.inclusion_tag('exptracker/tag_messages.html',takes_context=True)
#def show_message_panel(context):
#    logging.debug("WSA: showing message panel")
#    return messages