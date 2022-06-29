from builtins import object

from common.models import School
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator
from django_countries.widgets import CountrySelectWidget


class OrganisationForm(forms.ModelForm):
    class Meta(object):

        model = School
        fields = ["name", "postcode", "country"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Name of school or club"}),
            "postcode": forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Postcode / Zipcode"}),
            "country": CountrySelectWidget(layout="{widget}"),
        }
        help_texts = {"name": "Name of school or club", "postcode": "Postcode / Zipcode", "country": "Country"}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.current_school = kwargs.pop("current_school", None)
        super(OrganisationForm, self).__init__(*args, **kwargs)
        self.fields["postcode"].strip = False

    def clean(self):
        name = self.cleaned_data.get("name", None)
        postcode = self.cleaned_data.get("postcode", None)

        if name and postcode:
            try:
                school = School.objects.get(name=name, postcode=postcode)
            except ObjectDoesNotExist:
                return self.cleaned_data

            if not self.current_school or self.current_school.id != school.id:
                raise forms.ValidationError("There is already a school or club registered with that name and postcode")

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

    def clean_postcode(self):
        postcode = self.cleaned_data.get("postcode", None)

        if postcode:
            if len(postcode.replace(" ", "")) > 10 or len(postcode.replace(" ", "")) == 0:
                raise forms.ValidationError("Please enter a valid postcode or ZIP code")

        return postcode
