from builtins import object

from common.models import School
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator
from django_countries.widgets import CountrySelectWidget


class OrganisationForm(forms.ModelForm):
    county = forms.ChoiceField(
        choices=[
            (None, "(select county)"),
            # England
            ("Avon", "Avon"),
            ("Bath and North East Somerset", "Bath and North East Somerset"),
            ("Bedfordshire", "Bedfordshire"),
            ("Bedford", "Bedford"),
            ("Berkshire", "Berkshire"),
            ("Blackburn with Darwen", "Blackburn with Darwen"),
            ("Blackpool", "Blackpool"),
            ("Bournemouth, Christchurch and Poole", "Bournemouth, Christchurch and Poole"),
            ("Bournemouth", "Bournemouth"),
            ("Brighton and Hove", "Brighton and Hove"),
            ("Bristol", "Bristol"),
            ("Buckinghamshire", "Buckinghamshire"),
            ("Cambridgeshire", "Cambridgeshire"),
            ("Cambridgeshire and Isle of Ely", "Cambridgeshire and Isle of Ely"),
            ("Central Bedfordshire", "Central Bedfordshire"),
            ("Cheshire", "Cheshire"),
            ("Cheshire East", "Cheshire East"),
            ("Cheshire West and Chester", "Cheshire West and Chester"),
            ("Cleveland", "Cleveland"),
            ("Cornwall", "Cornwall"),
            ("Cumberland", "Cumberland"),
            ("Cumbria", "Cumbria"),
            ("Darlington", "Darlington"),
            ("Derbyshire", "Derbyshire"),
            ("Derby", "Derby"),
            ("Devon", "Devon"),
            ("Dorset", "Dorset"),
            ("Durham (County Durham)", "Durham (County Durham)"),
            ("East Suffolk", "East Suffolk"),
            ("East Sussex", "East Sussex"),
            ("Essex", "Essex"),
            ("Gloucestershire", "Gloucestershire"),
            ("Greater London", "Greater London"),
            ("Greater Manchester", "Greater Manchester"),
            ("Hampshire", "Hampshire"),
            ("Halton", "Halton"),
            ("Hartlepool", "Hartlepool"),
            ("Hereford and Worcester", "Hereford and Worcester"),
            ("Herefordshire", "Herefordshire"),
            ("Hertfordshire", "Hertfordshire"),
            ("Humberside", "Humberside"),
            ("Huntingdon and Peterborough", "Huntingdon and Peterborough"),
            ("Huntingdonshire", "Huntingdonshire"),
            ("Isle of Ely", "Isle of Ely"),
            ("Isle of Wight", "Isle of Wight"),
            ("Kent", "Kent"),
            ("Kingston upon Hull", "Kingston upon Hull"),
            ("Lancashire", "Lancashire"),
            ("Leicestershire", "Leicestershire"),
            ("Leicester", "Leicester"),
            ("Lincolnshire", "Lincolnshire"),
            ("Lincolnshire, Parts of Holland", "Lincolnshire, Parts of Holland"),
            ("Lincolnshire, Parts of Kesteven", "Lincolnshire, Parts of Kesteven"),
            ("Lincolnshire, Parts of Lindsey", "Lincolnshire, Parts of Lindsey"),
            ("London", "London"),
            ("City of London", "City of London"),
            ("Luton", "Luton"),
            ("Medway", "Medway"),
            ("Merseyside", "Merseyside"),
            ("Middlesbrough", "Middlesbrough"),
            ("Middlesex", "Middlesex"),
            ("Milton Keynes", "Milton Keynes"),
            ("Norfolk", "Norfolk"),
            ("Northamptonshire", "Northamptonshire"),
            ("North East Lincolnshire", "North East Lincolnshire"),
            ("North Humberside", "North Humberside"),
            ("North Lincolnshire", "North Lincolnshire"),
            ("North Northamptonshire", "North Northamptonshire"),
            ("North Somerset", "North Somerset"),
            ("Northumberland", "Northumberland"),
            ("North Yorkshire", "North Yorkshire"),
            ("Nottinghamshire", "Nottinghamshire"),
            ("Nottingham", "Nottingham"),
            ("Oxfordshire", "Oxfordshire"),
            ("Soke of Peterborough", "Soke of Peterborough"),
            ("Peterborough", "Peterborough"),
            ("Plymouth", "Plymouth"),
            ("Poole", "Poole"),
            ("Portsmouth", "Portsmouth"),
            ("Redcar and Cleveland", "Redcar and Cleveland"),
            ("Rutland", "Rutland"),
            ("Shropshire", "Shropshire"),
            ("Somerset", "Somerset"),
            ("Southampton", "Southampton"),
            ("Southend-on-Sea", "Southend-on-Sea"),
            ("South Humberside", "South Humberside"),
            ("South Gloucestershire", "South Gloucestershire"),
            ("South Yorkshire", "South Yorkshire"),
            ("Staffordshire", "Staffordshire"),
            ("Stockton-on-Tees", "Stockton-on-Tees"),
            ("Stoke-on-Trent", "Stoke-on-Trent"),
            ("Suffolk", "Suffolk"),
            ("Surrey", "Surrey"),
            ("Sussex", "Sussex"),
            ("Swindon", "Swindon"),
            ("Telford and Wrekin", "Telford and Wrekin"),
            ("Thurrock", "Thurrock"),
            ("Torbay", "Torbay"),
            ("Tyne and Wear", "Tyne and Wear"),
            ("Warrington", "Warrington"),
            ("Warwickshire", "Warwickshire"),
            ("West Midlands", "West Midlands"),
            ("Westmorland", "Westmorland"),
            ("Westmorland and Furness", "Westmorland and Furness"),
            ("West Northamptonshire", "West Northamptonshire"),
            ("West Suffolk", "West Suffolk"),
            ("West Sussex", "West Sussex"),
            ("West Yorkshire", "West Yorkshire"),
            ("Wiltshire", "Wiltshire"),
            ("Worcestershire", "Worcestershire"),
            ("Yorkshire", "Yorkshire"),
            ("Yorkshire, East Riding", "Yorkshire, East Riding"),
            ("Yorkshire, North Riding", "Yorkshire, North Riding"),
            ("Yorkshire, West Riding", "Yorkshire, West Riding"),
            ("York", "York"),
            # Northern Ireland
            ("Antrim", "Antrim"),
            ("Armagh", "Armagh"),
            ("City of Belfast", "City of Belfast"),
            ("Down", "Down"),
            ("Fermanagh", "Fermanagh"),
            ("Londonderry", "Londonderry"),
            ("City of Derry", "City of Derry"),
            ("Tyrone", "Tyrone"),
            # Scotland
            ("City of Aberdeen", "City of Aberdeen"),
            ("Aberdeenshire", "Aberdeenshire"),
            ("Angus (Forfarshire)", "Angus (Forfarshire)"),
            ("Argyll", "Argyll"),
            ("Ayrshire", "Ayrshire"),
            ("Banffshire", "Banffshire"),
            ("Berwickshire", "Berwickshire"),
            ("Bute", "Bute"),
            ("Caithness", "Caithness"),
            ("Clackmannanshire", "Clackmannanshire"),
            ("Cromartyshire", "Cromartyshire"),
            ("Dumfriesshire", "Dumfriesshire"),
            ("Dunbartonshire (Dumbarton)", "Dunbartonshire (Dumbarton)"),
            ("City of Dundee", "City of Dundee"),
            ("East Lothian (Haddingtonshire)", "East Lothian (Haddingtonshire)"),
            ("City of Edinburgh", "City of Edinburgh"),
            ("Fife", "Fife"),
            ("City of Glasgow", "City of Glasgow"),
            ("Inverness-shire", "Inverness-shire"),
            ("Kincardineshire", "Kincardineshire"),
            ("Kinross-shire", "Kinross-shire"),
            ("Kirkcudbrightshire", "Kirkcudbrightshire"),
            ("Lanarkshire", "Lanarkshire"),
            ("Midlothian (County of Edinburgh)", "Midlothian (County of Edinburgh)"),
            ("Moray (Elginshire)", "Moray (Elginshire)"),
            ("Nairnshire", "Nairnshire"),
            ("Orkney", "Orkney"),
            ("Peeblesshire", "Peeblesshire"),
            ("Perthshire", "Perthshire"),
            ("Renfrewshire", "Renfrewshire"),
            ("Ross and Cromarty", "Ross and Cromarty"),
            ("Ross-shire", "Ross-shire"),
            ("Roxburghshire", "Roxburghshire"),
            ("Selkirkshire", "Selkirkshire"),
            ("Shetland (Zetland)", "Shetland (Zetland)"),
            ("Stirlingshire", "Stirlingshire"),
            ("Sutherland", "Sutherland"),
            ("West Lothian (Linlithgowshire)", "West Lothian (Linlithgowshire)"),
            ("Wigtownshire", "Wigtownshire"),
            # Wales
            ("Anglesey", "Anglesey"),
            ("Brecknockshire", "Brecknockshire"),
            ("Caernarfonshire", "Caernarfonshire"),
            ("Cardiganshire", "Cardiganshire"),
            ("Carmarthenshire", "Carmarthenshire"),
            ("Clwyd", "Clwyd"),
            ("Denbighshire", "Denbighshire"),
            ("Dyfed", "Dyfed"),
            ("Flintshire", "Flintshire"),
            ("Glamorgan", "Glamorgan"),
            ("Gwent", "Gwent"),
            ("Gwynedd", "Gwynedd"),
            ("Merionethshire", "Merionethshire"),
            ("Mid Glamorgan", "Mid Glamorgan"),
            ("Monmouthshire", "Monmouthshire"),
            ("Montgomeryshire", "Montgomeryshire"),
            ("Pembrokeshire", "Pembrokeshire"),
            ("Powys", "Powys"),
            ("Radnorshire", "Radnorshire"),
            ("South Glamorgan", "South Glamorgan"),
            ("West Glamorgan", "West Glamorgan"),
            ("Wrexham", "Wrexham"),
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
