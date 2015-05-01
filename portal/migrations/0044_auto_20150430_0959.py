# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from portal.helpers import location

class Migration(migrations.Migration):

    def populate_country(apps, schema_editor):

        School = apps.get_model("portal", "School")
        for school in School.objects.all():
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
