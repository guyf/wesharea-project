from django import forms
from django.forms import ModelForm, TextInput, Textarea, HiddenInput
from django.contrib.auth.models import User
from groupmanager.models import Group
from emailregistration.forms import EmailRegistrationForm


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'desc_short', 'desc_long')
        widgets = {'name': TextInput(attrs={'class': 'sename','placeholder': 'Name'}),
                   'desc_short': TextInput(attrs={'class': 'sedesc','placeholder': 'Short Description'}),
                   'desc_long': Textarea(attrs={'class': 'sedesc','placeholder': 'Long Description'}),}


