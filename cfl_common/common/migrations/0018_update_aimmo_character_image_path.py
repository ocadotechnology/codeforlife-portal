from common.helpers.data_migration_loader import load_data_from_file
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("common", "0017_copy_email_to_username")]

    operations = [
        migrations.AddField(
            "AimmoCharacter",
            "alt",
            models.CharField(max_length=255, null=True),
        ),
    ]
