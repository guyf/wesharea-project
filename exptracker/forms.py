from django import forms
from django.forms import ModelForm, TextInput, Field
from django.contrib.auth.models import User
from registration.forms import RegistrationForm
from exptracker.models import SharedExpense, ExpenseItem #, Payment
from django.forms.models import modelformset_factory #,inlineformset_factory


class SharedExpenseForm(ModelForm):
    class Meta:
        model = SharedExpense
        fields = ('se_type','name', 'currency', 'desc', 'start_date')
        widgets = {'name': TextInput(attrs={'class': 'sename','placeholder': 'Name'}),
                   'currency': TextInput(attrs={'class': 'securrency','placeholder': u'\u0024\u00A3\u003F'}),
                   'desc': TextInput(attrs={'class': 'sedesc','placeholder': 'Description'}),
                   'paid_date': TextInput(attrs={'class': 'date','placeholder': 'Date Started'})}

SharedExpenseFormSetBase = modelformset_factory(
        SharedExpense,
        form=SharedExpenseForm,
        extra=1
)

class SharedExpenseFormSet(SharedExpenseFormSetBase):
    def add_fields(self, form, index):
        super(SharedExpenseFormSet, self).add_fields(form, index)




class ExpenseItemForm(ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ('name','desc','amount','paid_date')
        widgets = {'name': TextInput(attrs={'class': 'einame','placeholder': 'Name'}),
                   'desc': TextInput(attrs={'class': 'eidesc','placeholder': 'Description'}),
                   'amount': TextInput(attrs={'class': 'currency eiamount','placeholder': 'Amount'}),
                   'paid_date': TextInput(attrs={'class': 'date','placeholder': 'Date Paid'})}

ExpenseItemFormSetBase = modelformset_factory(
        ExpenseItem,
        form=ExpenseItemForm,
        extra=1,
        can_delete=True
)


class ExpenseItemFormSet(ExpenseItemFormSetBase):
    def add_fields(self, form, index):
        super(ExpenseItemFormSet, self).add_fields(form, index)


#class ExpenseItemInlineFormSet(ExpenseItemInlineFormSetBase):
#    def add_fields(self, form, index):
#        super(ExpenseItemInlineFormSet, self).add_fields(form, index)

#ExpenseItemInlineFormSetBase = inlineformset_factory(
#        SharedExpense,
#        ExpenseItem,
#        form=ExpenseItemForm, seems inlineformset_factory can't create from a form definition, so need to include fields...
#        fields = ('creditor', 'name', 'desc', 'amount', 'paid_date'),
#        extra=1,
#        can_delete=True
#        widgets = {'name': TextInput(attrs={'placeholder': 'Name'}),
#                   'desc': TextInput(attrs={'placeholder': 'Description'}),
#                   'amount': TextInput(attrs={'placeholder': 'Amount'}),
#                   'paid_date': TextInput(attrs={'placeholder': 'Date Paid'})}

#class MakePaymentForm(ModelForm):
#    class Meta:
#        model = Payment
#        fields = ('amount','desc')
#        widgets = {'amount': TextInput(attrs={'class': 'currency','placeholder': 'Amount'}),
#                   'desc': TextInput(attrs={'placeholder': 'Description'})}

#class ConfirmPaymentForm(ModelForm):
#    class Meta:
#        model = Payment
#        fields = ('confirm_receipt')
#)

#ConfirmPaymentFormSetBase = modelformset_factory(
#        Payment,
#        form=ConfirmPaymentForm,
#        extra=0
#)

#class ConfirmPaymentFormSet(ConfirmPaymentFormSetBase):
#    def add_fields(self, form, index):
#        super(ConfirmPaymentFormSet, self).add_fields(form, index)
