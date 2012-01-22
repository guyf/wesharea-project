import logging
from django.conf import settings
from django.contrib import messages
#from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from exptracker.models import SharedExpense, ExpenseItem #, Payment
from exptracker.forms import SharedExpenseForm, ExpenseItemForm, ExpenseItemFormSet #,MakePaymentForm
from groupmanager.models import Group
from browserutils import detect_browser

#TODO: find all the direct references into group manager model and decouple further


@login_required
def viewsharedexpense(request, sharedexpense_id):
	
    logging.info("WSA: New %s to sharedexpense view with sharedexpense id %s:" % (request.method, sharedexpense_id))
  
    try: se = SharedExpense.objects.get(pk=sharedexpense_id)
    except ObjectDoesNotExist:
        messages.error(request, 'Sorry that shared expense does not exist, if you think it should please let us know.')
        return redirect('welcome')

    try: g = se.group
    except ObjectDoesNotExist:
        messages.error(request, 'Sorry we could not find the group associated with the sharedexpense, if you think it should please let us know.')
        return redirect('welcome')
    
    if se.is_participant(request.user):
        logging.info("WSA: user %s is a participant of sharedexpense %s." % (request.user.username, sharedexpense_id))
        is_org = False
    elif se.is_organiser(request.user):
        logging.info("WSA: user %s is the organiser of sharedexpense %s." % (request.user.username, sharedexpense_id))
        is_org = True
    else:
        logging.info("WSA: user %s does not have permission to view this sharedexpense %s" % (request.user.username, sharedexpense_id))
        messages.error(request, 'Sorry you do not have permission to see that shared expense, the organiser may have removed you from the group. Please contact the organiser and if that is not the problem let us know.')
        return redirect('welcome')

    participants = []
    participants.append(se.get_organiser())
    participants.extend(list(se.get_participants()))
    logging.debug("WSA: participants %s of sharedexpense %s" % (participants, sharedexpense_id))

    return render_to_response('exptracker/sharedexpense.html', {'sharedexpense': se, 'group': g, 'participants':participants, 'is_org': is_org },context_instance=RequestContext(request))

@login_required
def createsharedexpense(request):

    if request.method == 'POST':     
        se_form = SharedExpenseForm(request.POST)
        if  se_form.is_valid():
            se = se_form.save(commit=False)
            g = Group(name=str('for shared expense: ' + se.name), organiser=request.user)
            g.save()	
            se.group_id = g.id
            se.save()
            return HttpResponseRedirect(reverse('view_sharedexpense', args=[se.id]))
        else:
            messages.error(request, 'Your new shared expense was not created please see below for more information. If you think this error should not have occurred please let us know.')
    else:  
        se_form = SharedExpenseForm()

    return render_to_response("exptracker/edit_sharedexpense.html",{'sharedexpense_form':se_form },context_instance=RequestContext(request))

@login_required
def updatesharedexpense(request, sharedexpense_id):

    if request.method == 'POST':     
        se = get_object_or_404(SharedExpense, pk=sharedexpense_id)
        se_form = SharedExpenseForm(request.POST, instance=se)
        if  se_form.is_valid():
            se = se_form.save(commit=False)
            g = get_object_or_404(Group, pk=se.group_id)
            g.name = str('group for sharedexpense: ' + se.name)
            g.save()
            se.save()
            return HttpResponseRedirect(reverse('view_sharedexpense', args=[se.id]))
        else:
            messages.error(request, 'Your shared expense was not updated, see below for more information. If you think this error should not have occurred please let us know.')
    else:  
        se = get_object_or_404(SharedExpense, pk=sharedexpense_id)
        se_form = SharedExpenseForm(instance=se)

    return render_to_response("exptracker/edit_sharedexpense.html",{'sharedexpense': se, 'sharedexpense_form':se_form },context_instance=RequestContext(request))


@login_required
def updateexpenseitems(request, sharedexpense_id, user_id):

    if request.method == 'POST':
        se = get_object_or_404(SharedExpense, pk=sharedexpense_id)
        if se.is_participant(request.user) or  se.is_organiser(request.user):
            user = get_object_or_404(User, pk=user_id)
            expenseitem_formset = ExpenseItemFormSet(request.POST, prefix=user_id)
            logging.debug("WSA: EI Form %s" % str(expenseitem_formset))
            if expenseitem_formset.is_valid():
                expenseitems = expenseitem_formset.save(commit=False)
                for expenseitem in expenseitems:
                    #add in the mandatory fields not collected on form sharedexpense and creditor
                    expenseitem.sharedexpense = se
                    expenseitem.creditor = user
                    expenseitem.save()
                    logging.info("WSA: Added Expenseitem %s to Sharedexpense %s" % (expenseitem.name, se.name))
            else:
                #TODO: this needs unpicking so form errors can be passed back to the template. The customer tag is curently creating a new form instance.
                logging.info("WSA: Failed to add new Expenseitems to Sharedexpense %s with error %s" % (se.name, str(expenseitem_formset.errors)))
                messages.error(request, 'Your expense items did not update. Each items requires at least a name, a value and a valid date. If you think this error should not have occurred please let us know.')

#    if request.is_ajax():
        #expenseitem_formset = ExpenseItemFormSet(queryset=ExpenseItem.objects.all().filter(sharedexpense=se).filter(creditor=user), prefix=user.username)
#        rdict={'msg':'updated successfully'}
#        logging.info("WSA: Upated shared expense via AJAX")
#        return HttpResponse(simplejson.dumps(rdict), mimetype='application/javascript')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
@csrf_exempt	
def wsaremoveparticipant(request, sharedexpense_id, user_id):

    logging.debug("WSA: remove user for sharedexpense %s and user %s" % (sharedexpense_id, user_id))
    sharedexpense = get_object_or_404(SharedExpense, pk=sharedexpense_id)
    if sharedexpense.is_organiser(request.user):
        user = get_object_or_404(User, pk=user_id)
        #check they have a zero balance
        if sharedexpense.participant_balance(user) != 0:
            logging.info("WSA: %s was not removed from Sharedexpense %s as balance was %s" % (user.first_name, sharedexpense.name, sharedexpense.participant_balance(user)))
            messages.error(request, 'You cannot remove a participant unless their balance is zero.')
            messages.info(request, 'You can record a balancing payment between any two members of your group by entering a negative expense for the one receiving money and an equal positive expense for the one paying money.')
        else:
            #remove their expense items
            sharedexpense.remove_expenseitems(user)
            sharedexpense.save()
            logging.info("WSA: Removed participant %s from Sharedexpense %s" % (user.username, sharedexpense.name))
            sharedexpense.group.remove_participant(user)
    else:
        logging.info("WSA: removeparticipant decided %s was not organiser of Sharedexpense %s" % (request.user.username, sharedexpense.name))
        messages.error(request, 'You cannot remove participants from this shared expense, if you think this error should not have occurred please let us know.')
	
    return HttpResponseRedirect(reverse('view_sharedexpense', args=[sharedexpense_id]))


@login_required		
def makepayment(request, sharedexpense_id, user_id):

    if request.method == 'POST':
        sharedexpense = get_object_or_404(SharedExpense, pk=sharedexpense_id)
        if sharedexpense.is_participant(request.user) or sharedexpense.is_organiser(request.user):
            recipient = get_object_or_404(User, pk=user_id)
#            makepayment_form = MakePaymentForm(request.POST)
#            if makepayment_form.is_valid():
#                #add in the mandatory fields not collected on form sharedexpense and creditor
#                payment = makepayment_form.save(commit=False)
#                payment.sharedexpense = sharedexpense
#                payment.payer = request.user
#                payment.recipient = user
#                payment.save()
#                logging.info("WSA: Added Payment from %s to %s for Sharedexpense %s" % (request.user.username, user.username, sharedexpense.name))
#            else:
#                logging.info("WSA: Failed to add Payment from %s to %s for Sharedexpense %s" % (request.user.username, user.username, sharedexpense.name))
#	             #TODO: find out why and tell them
#                messages.error(request, 'Your payment failed because: %s, if you think this error should not have occurred please let us know.' % str(makepayment_form.errors))
            expensepayment_form = ExpenseItemForm(request.POST)
            logging.debug("WSA: payment form: %s" % expensepayment_form)
            if expensepayment_form.is_valid():
                payer_ei = expensepayment_form.save(commit=False)
                payer_ei.sharedexpense = sharedexpense
                payer_ei.creditor = request.user
                payer_ei.desc = 'payment to ' + str(recipient.first_name)
                #set these flags true for now might use them properly later
                payer_ei.is_payment = True
                payer_ei.is_confirmedpayment = True
                payer_ei.save()
                recipient_ei = ExpenseItem(sharedexpense = sharedexpense, creditor = recipient, name = payer_ei.name, desc = str('payment from ' + request.user.first_name), amount = (payer_ei.amount * -1), is_payment = True, is_confirmedpayment = True)
                recipient_ei.save()
                logging.info("WSA: Added Payment from %s to %s for Sharedexpense %s" % (request.user.username, recipient.username, sharedexpense.name))
            else:
                logging.info("WSA: Failed to add Payment from %s to %s for Sharedexpense %s" % (request.user.username, recipient.username, sharedexpense.name))
	            #TODO: find out why and tell them
                messages.error(request, 'Your payment did not save. Each payment requires a name and value. if you think this error should not have occurred please let us know.' % str(expensepayment_form.errors))
        else:
            logging.info("WSA: addpayment decided %s was not a participant or organiser Sharedexpense %s" % (request.user.username, sharedexpense.name))
            messages.error(request, 'You cannot make payment to people not part of this shared expense, if you think this error should not have occurred please let us know.')
	
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

#@login_required		
#def confirmpayment(request, sharedexpense_id, payment_id):

#    if request.method == 'POST':
#        payment = get_object_or_404(Payment, pk=payment_id)
#        if payment.recipient.username == request.user.username:
#            payment.receipt_confirmed = True
#            payment.save()
#            logging.info("WSA: Confirmed Payment of %s to %s for Sharedexpense %s." % (str(payment.amount), request.user.username, sharedexpense_id))
#        else:
#            logging.info("WSA: Failed to Confirm Payment of %s to %s for Sharedexpense %s" % (str(payment.amount), request.user.username, sharedexpense_id))
            #TODO: find out why and tell them
#            messages.error(request, 'Failed to confirm payment please try again, if you think this error should not have occurred please let us know.')

#    return HttpResponseRedirect(request.META['HTTP_REFERER'])
		
#def xd_receiver(request):
#    return render_to_response('facebook/xd_receiver.htm')