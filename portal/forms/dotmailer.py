from django import forms


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        label="Sign up to our newsletter",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Your email address",
                "id": "newsletter_email_field",
            }
        ),
        help_text="Enter email address above",
    )


class ConsentForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "your.name@yourdomain.com",
            }
        ),
    )

    consent_ticked = forms.BooleanField(
        widget=forms.CheckboxInput(), initial=False, required=True
    )
