from django import forms
from django.forms import ModelForm, TextInput, HiddenInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

#borrowed widget for email input from http://www.peterbe.com/plog/emailinput-html5-django
class EmailInput(forms.widgets.Input): 
    input_type = 'email'

    def render(self, name, value, attrs=None): 
        if attrs is None: 
            attrs = {} 
        attrs.update(dict(autocorrect='off', 
                          autocapitalize='off', 
                          spellcheck='false')) 
        return super(EmailInput, self).render(name, value, attrs=attrs)


class EmailAuthenticationForm(forms.Form):
    username = forms.EmailField(label='Email address', widget=EmailInput(attrs={'class': 'username','placeholder': 'Email address'}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'password','placeholder': 'Password'}, render_value=False))

        
class EmailRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label=_("Email"), widget=EmailInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Firstname'}))
    last_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Lastname'}))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'password','placeholder': 'Password'}, render_value=False))
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput(attrs={'class': 'password','placeholder': 'Password (again)'}, render_value=False),
        help_text = _("Enter the same password as above, for verification."))
 
    class Meta:
        model = User
        fields = ("email",)
 
    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.filter(email=email)
        if users.count() > 0:
            raise forms.ValidationError("That email is already in use in the system.")
        return email
 
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
        

class EmailInvitationForm(forms.ModelForm):
    email = forms.EmailField(label=_("Email"), widget=EmailInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Firstname'}))
    last_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Lastname'}))
 
    class Meta:
        model = User
        fields = ("email",)
 
    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.filter(email=email)
        if users.count() > 0:
            raise forms.ValidationError("That email is already in use in the system.")
        return email

class EmailInviteAcceptForm(forms.Form):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'password','placeholder': 'Password'}, render_value=False))
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput(attrs={'class': 'password','placeholder': 'Password (again)'}, render_value=False),
        help_text = _("Enter the same password as above, for verification."))
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
 
