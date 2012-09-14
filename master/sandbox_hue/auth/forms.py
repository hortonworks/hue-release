from django import forms
from registration.forms import RegistrationFormUniqueEmail


class RegistrationFormProfile(RegistrationFormUniqueEmail):
	work = forms.CharField(label = 'Phone number')