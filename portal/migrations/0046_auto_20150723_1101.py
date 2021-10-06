from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("portal", "0045_auto_20150430_1446")]

    operations = [
        migrations.AlterModelOptions(
            name="school",
            options={
                "permissions": (
                    ("view_aggregated_data", "Can see available aggregated data"),
                    ("view_map_data", "Can see schools' location displayed on map"),
                )
            },
        )
    ]
