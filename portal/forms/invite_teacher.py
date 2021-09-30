from django import forms


class InviteTeacherForm(forms.Form):

    email_regex = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "recipient.name@domain.com",
                "id": "newsletter_email_field",
                "pattern": email_regex,
                "type": "email",
            }
        )
    )
