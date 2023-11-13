from builtins import object

from common.models import School
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator
from django_countries.widgets import CountrySelectWidget


class OrganisationForm(forms.ModelForm):
    county = forms.ChoiceField(
        choices=[
            [None, "(select county)"],
            ["Aberdeen City", "Aberdeen City"],
            ["Aberdeenshire", "Aberdeenshire"],
            ["Angus", "Angus"],
            ["Argyll and Bute", "Argyll and Bute"],
            ["Bedfordshire", "Bedfordshire"],
            ["Belfast", "Belfast"],
            ["Belfast Greater", "Belfast Greater"],
            ["Berkshire", "Berkshire"],
            ["Blaenau Gwent", "Blaenau Gwent"],
            ["Bridgend", "Bridgend"],
            ["Buckinghamshire", "Buckinghamshire"],
            ["Caerphilly", "Caerphilly"],
            ["Cambridgeshire", "Cambridgeshire"],
            ["Cardiff", "Cardiff"],
            ["Carmarthenshire", "Carmarthenshire"],
            ["Ceredigion", "Ceredigion"],
            ["Channel Islands", "Channel Islands"],
            ["Cheshire", "Cheshire"],
            ["City of Edinburgh", "City of Edinburgh"],
            ["Clackmannanshire", "Clackmannanshire"],
            ["Conwy", "Conwy"],
            ["Cornwall", "Cornwall"],
            ["County Antrim", "County Antrim"],
            ["County Armagh", "County Armagh"],
            ["County Down", "County Down"],
            ["County Fermanagh", "County Fermanagh"],
            ["County Londonderry", "County Londonderry"],
            ["County Tyrone", "County Tyrone"],
            ["County of Bristol", "County of Bristol"],
            ["Cumbria", "Cumbria"],
            ["Denbighshire", "Denbighshire"],
            ["Derbyshire", "Derbyshire"],
            ["Devon", "Devon"],
            ["Dorset", "Dorset"],
            ["Dumfries and Galloway", "Dumfries and Galloway"],
            ["Dunbartonshire", "Dunbartonshire"],
            ["Dundee City", "Dundee City"],
            ["Durham", "Durham"],
            ["East Ayrshire", "East Ayrshire"],
            ["East Dunbartonshire", "East Dunbartonshire"],
            ["East Lothian", "East Lothian"],
            ["East Renfrewshire", "East Renfrewshire"],
            ["East Riding of Yorkshire", "East Riding of Yorkshire"],
            ["East Sussex", "East Sussex"],
            ["Essex", "Essex"],
            ["Falkirk", "Falkirk"],
            ["Fife", "Fife"],
            ["Flintshire", "Flintshire"],
            ["Glasgow City", "Glasgow City"],
            ["Gloucestershire", "Gloucestershire"],
            ["Greater London", "Greater London"],
            ["Greater Manchester", "Greater Manchester"],
            ["Guernsey Channel Islands", "Guernsey Channel Islands"],
            ["Gwynedd", "Gwynedd"],
            ["Hampshire", "Hampshire"],
            ["Hereford and Worcester", "Hereford and Worcester"],
            ["Herefordshire", "Herefordshire"],
            ["Hertfordshire", "Hertfordshire"],
            ["Highland", "Highland"],
            ["Inverclyde", "Inverclyde"],
            ["Inverness", "Inverness"],
            ["Isle of Anglesey", "Isle of Anglesey"],
            ["Isle of Barra", "Isle of Barra"],
            ["Isle of Man", "Isle of Man"],
            ["Isle of Wight", "Isle of Wight"],
            ["Jersey Channel Islands", "Jersey Channel Islands"],
            ["Kent", "Kent"],
            ["Lancashire", "Lancashire"],
            ["Leicestershire", "Leicestershire"],
            ["Lincolnshire", "Lincolnshire"],
            ["Merseyside", "Merseyside"],
            ["Merthyr Tydfil", "Merthyr Tydfil"],
            ["Midlothian", "Midlothian"],
            ["Monmouthshire", "Monmouthshire"],
            ["Moray", "Moray"],
            ["Neath Port Talbot", "Neath Port Talbot"],
            ["Newport", "Newport"],
            ["Norfolk", "Norfolk"],
            ["North Ayrshire", "North Ayrshire"],
            ["North Lanarkshire", "North Lanarkshire"],
            ["North Yorkshire", "North Yorkshire"],
            ["Northamptonshire", "Northamptonshire"],
            ["Northumberland", "Northumberland"],
            ["Nottinghamshire", "Nottinghamshire"],
            ["Orkney", "Orkney"],
            ["Orkney Islands", "Orkney Islands"],
            ["Oxfordshire", "Oxfordshire"],
            ["Pembrokeshire", "Pembrokeshire"],
            ["Perth and Kinross", "Perth and Kinross"],
            ["Powys", "Powys"],
            ["Renfrewshire", "Renfrewshire"],
            ["Rhondda Cynon Taff", "Rhondda Cynon Taff"],
            ["Rutland", "Rutland"],
            ["Scottish Borders", "Scottish Borders"],
            ["Shetland Islands", "Shetland Islands"],
            ["Shropshire", "Shropshire"],
            ["Somerset", "Somerset"],
            ["South Ayrshire", "South Ayrshire"],
            ["South Lanarkshire", "South Lanarkshire"],
            ["South Yorkshire", "South Yorkshire"],
            ["Staffordshire", "Staffordshire"],
            ["Stirling", "Stirling"],
            ["Suffolk", "Suffolk"],
            ["Surrey", "Surrey"],
            ["Swansea", "Swansea"],
            ["Torfaen", "Torfaen"],
            ["Tyne and Wear", "Tyne and Wear"],
            ["Vale of Glamorgan", "Vale of Glamorgan"],
            ["Warwickshire", "Warwickshire"],
            ["West Dunbart", "West Dunbart"],
            ["West Lothian", "West Lothian"],
            ["West Midlands", "West Midlands"],
            ["West Sussex", "West Sussex"],
            ["West Yorkshire", "West Yorkshire"],
            ["Western Isles", "Western Isles"],
            ["Wiltshire", "Wiltshire"],
            ["Worcestershire", "Worcestershire"],
            ["Wrexham", "Wrexham"],
        ],
        required=False,
        help_text="County (optional)",
    )

    class Meta(object):
        model = School
        fields = ["name", "country", "county"]
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
