from django import forms


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        label="Sign up to receive updates about Code for Life games and teaching resources.",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Your email address",
                "id": "newsletter_email_field",
            }
        ),
        help_text="Enter email address above",
    )

    age_verification = forms.BooleanField(
        widget=forms.CheckboxInput(), initial=False, required=True
    )


class ConsentForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={"placeholder": "your.name@yourdomain.com"}
        ),
    )

    consent_ticked = forms.BooleanField(
        widget=forms.CheckboxInput(), initial=False, required=True
    )
