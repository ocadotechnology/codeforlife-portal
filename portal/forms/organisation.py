from django import forms

from portal.models import School

from django_countries.widgets import CountrySelectWidget
from  django.core.exceptions import ObjectDoesNotExist


class OrganisationForm(forms.ModelForm):

    class Meta:
        model = School
        fields = ['name', 'postcode', 'country']
        labels = {
            'name' : "Name of your school or club",
            'postcode' : 'Postcode',
            'country' : 'Country',
            }
        widgets = {
            'name' : forms.TextInput(attrs={'autocomplete': "off", 'placeholder': 'Name of your school or club'}),
            'postcode' : forms.TextInput(attrs={'autocomplete': "off", 'placeholder': 'Postcode'}),
            'country' : CountrySelectWidget(attrs={'class': 'wide'}),
            }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.current_school = kwargs.pop('current_school', None)
        if not self.current_school:
            current_password = forms.CharField(
                label='Enter your password',
                widget=forms.PasswordInput(attrs={'autocomplete': "off"}))

        super(OrganisationForm, self).__init__(*args, **kwargs)

    def clean(self):
        name = self.cleaned_data.get('name', None)
        postcode = self.cleaned_data.get('postcode', None)

        if name and postcode:
            try:
                school = School.objects.get(name=name, postcode=postcode)
            except ObjectDoesNotExist:
                return self.cleaned_data

            if not self.current_school or self.current_school.id != school.id:
                raise forms.ValidationError(
                    "There is already a school or club registered with that name and postcode")

        return self.cleaned_data

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode', None)

        if postcode:
            # Basic postcode check for now
            if (not (len(postcode.replace(' ', '')) >= 5 and len(postcode.replace(' ', '')) <= 8) or
                    not postcode.replace(' ', '').isalnum()):
                raise forms.ValidationError("That postcode was not recognised")

        return postcode

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password', None)
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Your password was incorrect")


class OrganisationJoinForm(forms.Form):
    fuzzy_name = forms.CharField(
        label="Search for school or club by name or postcode",
        widget=forms.TextInput(
            attrs={'placeholder': "Enrico Fermi High School"}))

    # Note: the reason this is a CharField rather than a ChoiceField is to avoid having to
    # provide choices which was problematic given that the options are dynamically generated.
    chosen_org = forms.CharField(
        label='Select school or club',
        widget=forms.Select(attrs={'class': 'wide'}))

    def clean_chosen_org(self):
        chosen_org = self.cleaned_data.get('chosen_org', None)

        if chosen_org and not School.objects.filter(id=int(chosen_org)).exists():
            raise forms.ValidationError("That school or club was not recognised")

        return chosen_org

