from django import forms
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth import forms as django_auth_forms
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from portal.models import Student, Teacher
import password_strength_test


class PasswordResetSetPasswordForm(django_auth_forms.SetPasswordForm):
    def __init__(self, user, *args, **kwags):
        super(PasswordResetSetPasswordForm, self).__init__(user, *args, **kwags)
        self.fields['new_password1'].label = "Enter your new password"
        self.fields['new_password1'].widget.attrs['placeholder'] = "Enter your new password"
        self.fields['new_password2'].label = "Confirm your new password"
        self.fields['new_password2'].widget.attrs['placeholder'] = "Confirm your new password"

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1', None)
        if hasattr(self.user.userprofile, 'teacher'):
            if not password_strength_test(new_password1):
                raise forms.ValidationError(
                    "Password not strong enough, consider using at least 8 characters, upper and "
                    + "lower case letters, and numbers")
        elif hasattr(self.user.userprofile, 'student'):
            if not password_strength_test(new_password1, length=6, upper=False, lower=False,
                                          numbers=False):
                raise forms.ValidationError(
                    "Password not strong enough, consider using at least 6 characters")
        return new_password1
