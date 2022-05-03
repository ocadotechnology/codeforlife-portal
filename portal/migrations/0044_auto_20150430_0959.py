from __future__ import unicode_literals

from builtins import str
from django.db import models, migrations


class Migration(migrations.Migration):

    # It will guess the country of the school using postcode, UK will be set if no result is returned by the API
    def populate_country(apps, schema_editor):

        School = apps.get_model("portal", "School")
        for school in School.objects.all():
            country, town, lat, lng = (
                "GB",
                "0",
                "0",
                "0",
            )
            school.country = str(country)
            school.town = town
            school.lat = lat
            school.lng = lng
            school.save()

    def reset_country(apps, schema_editor):
        School = apps.get_model("portal", "School")
        for school in School.objects.all():
            school.country = ""
            school.town = "0"
            school.lat = "0"
            school.lng = "0"
            school.save()

    dependencies = [("portal", "0043_auto_20150430_0952")]

    operations = [migrations.RunPython(populate_country, reset_country)]
