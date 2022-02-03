from django import forms


# This is the form that asks if the user wants to disable 2FA after clicking disable
# 2FA, setting it to always checked and hidden in CSS
class DisableForm(forms.Form):
    understand = forms.BooleanField(label="", initial=True)
