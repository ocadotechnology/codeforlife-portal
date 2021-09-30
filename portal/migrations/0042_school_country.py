from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("portal", "0001_squashed_0041_new_news")]

    operations = [
        migrations.AddField(
            model_name="school",
            name="country",
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        )
    ]
