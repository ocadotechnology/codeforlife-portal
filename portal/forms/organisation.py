from builtins import object

from common.models import School
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator
from django_countries.widgets import CountrySelectWidget


class OrganisationForm(forms.ModelForm):
    class Meta(object):
        model = School
        fields = ["name", "country"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Name of school or club"}),
            "country": CountrySelectWidget(layout="{widget}"),
        }
        help_texts = {
            "name": "Name of school or club",
            "country": "Country (optional)",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.current_school = kwargs.pop("current_school", None)
        super(OrganisationForm, self).__init__(*args, **kwargs)

    def clean(self):
        name = self.cleaned_data.get("name", None)

        if name:
            try:
                school = School.objects.get(name=name)
            except ObjectDoesNotExist:
                return self.cleaned_data

            if not self.current_school or self.current_school.id != school.id:
                raise forms.ValidationError("There is already a school or club registered with that name")

        return self.cleaned_data

    def clean_name(self):
        name = self.cleaned_data.get("name", None)
        validator = EmailValidator()

        if name:
            try:
                validator(name)
                is_email = True
            except forms.ValidationError:
                is_email = False

            if is_email:
                raise forms.ValidationError("Please make sure your organisation name is valid")

        return name
