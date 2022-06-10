from django import forms


class InviteTeacherForm(forms.Form):

    teacher_first_name = forms.CharField(
        help_text="Enter first name of teacher",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "First name of teacher"}),
    )
    teacher_last_name = forms.CharField(
        help_text="Enter last name of teacher",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Last name of teacher"}),
    )
    teacher_email = forms.EmailField(
        help_text="Enter email address",
        widget=forms.EmailInput(attrs={"autocomplete": "off", "placeholder": "Email address"}),
    )

    make_admin_ticked = forms.BooleanField(
        label="Make an administrator of the school",
        widget=forms.CheckboxInput(),
        initial=False,
        required=False,
    )


class InvitedTeacherForm(forms.Form):

    teacher_password = forms.CharField(
        help_text="Enter a password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Password"}),
    )
    teacher_confirm_password = forms.CharField(
        help_text="Repeat password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Repeat password"}),
    )

    newsletter_ticked = forms.BooleanField(widget=forms.CheckboxInput(), initial=False, required=False)
