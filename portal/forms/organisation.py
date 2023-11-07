from builtins import object

from common.models import School
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator
from django_countries.widgets import CountrySelectWidget


class OrganisationForm(forms.ModelForm):
    county = forms.ChoiceField(
        choices=[
            # England
            "Avon",
            "Bath and North East Somerset",
            "Bedfordshire",
            "Bedford",
            "Berkshire",
            "Blackburn with Darwen",
            "Blackpool",
            "Bournemouth, Christchurch and Poole",
            "Bournemouth",
            "Brighton and Hove",
            "Bristol",
            "Buckinghamshire",
            "Cambridgeshire",
            "Cambridgeshire and Isle of Ely",
            "Central Bedfordshire",
            "Cheshire",
            "Cheshire East",
            "Cheshire West and Chester",
            "Cleveland",
            "Cornwall",
            "Cumberland",
            "Cumbria",
            "Darlington",
            "Derbyshire",
            "Derby",
            "Devon",
            "Dorset",
            "Durham (County Durham)",
            "East Suffolk",
            "East Sussex",
            "Essex",
            "Gloucestershire",
            "Greater London",
            "Greater Manchester",
            "Hampshire",
            "Halton",
            "Hartlepool",
            "Hereford and Worcester",
            "Herefordshire",
            "Hertfordshire",
            "Humberside",
            "Huntingdon and Peterborough",
            "Huntingdonshire",
            "Isle of Ely",
            "Isle of Wight",
            "Kent",
            "Kingston upon Hull",
            "Lancashire",
            "Leicestershire",
            "Leicester",
            "Lincolnshire",
            "Lincolnshire, Parts of Holland",
            "Lincolnshire, Parts of Kesteven",
            "Lincolnshire, Parts of Lindsey",
            "London",
            "City of London",
            "Luton",
            "Medway",
            "Merseyside",
            "Middlesbrough",
            "Middlesex",
            "Milton Keynes",
            "Norfolk",
            "Northamptonshire",
            "North East Lincolnshire",
            "North Humberside",
            "North Lincolnshire",
            "North Northamptonshire",
            "North Somerset",
            "Northumberland",
            "North Yorkshire",
            "Nottinghamshire",
            "Nottingham",
            "Oxfordshire",
            "Soke of Peterborough",
            "Peterborough",
            "Plymouth",
            "Poole",
            "Portsmouth",
            "Redcar and Cleveland",
            "Rutland",
            "Shropshire",
            "Somerset",
            "Southampton",
            "Southend-on-Sea",
            "South Humberside",
            "South Gloucestershire",
            "South Yorkshire",
            "Staffordshire",
            "Stockton-on-Tees",
            "Stoke-on-Trent",
            "Suffolk",
            "Surrey",
            "Sussex",
            "Swindon",
            "Telford and Wrekin",
            "Thurrock",
            "Torbay",
            "Tyne and Wear",
            "Warrington",
            "Warwickshire",
            "West Midlands",
            "Westmorland",
            "Westmorland and Furness",
            "West Northamptonshire",
            "West Suffolk",
            "West Sussex",
            "West Yorkshire",
            "Wiltshire",
            "Worcestershire",
            "Yorkshire",
            "Yorkshire, East Riding",
            "Yorkshire, North Riding",
            "Yorkshire, West Riding",
            "York",
            # Northern Ireland
            "Antrim",
            "Armagh",
            "City of Belfast",
            "Down",
            "Fermanagh",
            "Londonderry",
            "City of Derry",
            "Tyrone",
            # Scotland
            "City of Aberdeen",
            "Aberdeenshire",
            "Angus (Forfarshire)",
            "Argyll",
            "Ayrshire",
            "Banffshire",
            "Berwickshire",
            "Bute",
            "Caithness",
            "Clackmannanshire",
            "Cromartyshire",
            "Dumfriesshire",
            "Dunbartonshire (Dumbarton)",
            "City of Dundee",
            "East Lothian (Haddingtonshire)",
            "City of Edinburgh",
            "Fife",
            "City of Glasgow",
            "Inverness-shire",
            "Kincardineshire",
            "Kinross-shire",
            "Kirkcudbrightshire",
            "Lanarkshire",
            "Midlothian (County of Edinburgh)",
            "Moray (Elginshire)",
            "Nairnshire",
            "Orkney",
            "Peeblesshire",
            "Perthshire",
            "Renfrewshire",
            "Ross and Cromarty",
            "Ross-shire",
            "Roxburghshire",
            "Selkirkshire",
            "Shetland (Zetland)",
            "Stirlingshire",
            "Sutherland",
            "West Lothian (Linlithgowshire)",
            "Wigtownshire",
            # Wales
            "Anglesey",
            "Brecknockshire",
            "Caernarfonshire",
            "Cardiganshire",
            "Carmarthenshire",
            "Clwyd",
            "Denbighshire",
            "Dyfed",
            "Flintshire",
            "Glamorgan",
            "Gwent",
            "Gwynedd",
            "Merionethshire",
            "Mid Glamorgan",
            "Monmouthshire",
            "Montgomeryshire",
            "Pembrokeshire",
            "Powys",
            "Radnorshire",
            "South Glamorgan",
            "West Glamorgan",
            "Wrexham",
        ],
        required=False,
    )

    class Meta(object):
        model = School
        fields = ["name", "country", "county"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Name of school or club"}),
            "country": CountrySelectWidget(layout="{widget}"),
            "county": forms.ChoiceWidget(choices=["a", "b"]),
        }
        help_texts = {
            "name": "Name of school or club",
            "country": "Country (optional)",
            "county": "County (optional)",
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
