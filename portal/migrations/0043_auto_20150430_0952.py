from __future__ import unicode_literals

from django.db import models, migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [("portal", "0042_school_country")]

    operations = [
        migrations.AlterField(
            model_name="school",
            name="country",
            field=django_countries.fields.CountryField(
                max_length=2, null=True, blank=True
            ),
        )
    ]
