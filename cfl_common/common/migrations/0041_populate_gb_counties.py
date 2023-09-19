import pgeocode
from django.db import migrations

from ..helpers.organisation import sanitise_uk_postcode


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0040_school_county"),
    ]

    def forwards(apps, schema_editor):
        """Populate the county field for schools in GB"""
        School = apps.get_model("common", "School")
        gb_schools = School.objects.filter(country="GB")
        nomi = pgeocode.Nominatim("GB")

        for school in gb_schools:
            if school.postcode.replace(" ", "") == "":
                school.county = "nan"
                school.save()
            else:
                county = nomi.query_postal_code(sanitise_uk_postcode(school.postcode)).county_name
                school.county = county
                school.save()

    operations = [migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop)]
