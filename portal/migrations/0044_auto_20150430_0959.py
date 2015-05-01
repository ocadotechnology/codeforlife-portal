# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from portal.helpers import location
from time import sleep

class Migration(migrations.Migration):

    # It will guess the country of the school using postcode, UK will be set if no result is returned by the API
    def populate_country(apps, schema_editor):

        School = apps.get_model("portal", "School")
        for school in School.objects.all():
            sleep(0.5)  # so we execute a bit less than 5/sec
            error, country = location.lookup_country(school.postcode)
            school.country = "%s" % country
            error, town, lat, lng = location.lookup_coord(school.postcode, country)
            school.town = town
            school.lat = lat
            school.lng = lng
            school.save()

    def reset_country(apps, schema_editor):
        School = apps.get_model("portal", "School")
        for school in School.objects.all():
            school.country = ''
            school.save()

    dependencies = [
        ('portal', '0043_auto_20150430_0952'),
    ]

    operations = [
        migrations.RunPython(populate_country, reset_country),
    ]
