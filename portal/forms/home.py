from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100,
                           widget=forms.TextInput(attrs={'class': 'contactField'}))
    telephone = forms.CharField(label='Telephone', max_length=50,
                                widget=forms.TextInput(attrs={'class': 'contactField'}))
    email = forms.EmailField(label='Email address',
                             widget=forms.TextInput(attrs={'class': 'contactField'}))
    message = forms.CharField(label='Message', max_length=250,
                              widget=forms.Textarea(attrs={'class': 'contactField'}))
    browser = forms.CharField(label='Browser', max_length=250, required=False,
                              widget=forms.TextInput(attrs={'type': 'hidden', 'id': 'browserField'})
                              )
