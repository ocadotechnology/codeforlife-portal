from common.helpers.data_migration_loader import load_data_from_file
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0004_add_aimmocharacters"),
        ("aimmo", "0020_add_info_to_worksheet"),
    ]

    operations = [
        migrations.RunPython(
            migrations.RunPython.noop, reverse_code=migrations.RunPython.noop
        )
    ]
