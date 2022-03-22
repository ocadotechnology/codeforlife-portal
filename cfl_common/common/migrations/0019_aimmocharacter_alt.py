from common.helpers.data_migration_loader import load_data_from_file
from django.db import migrations, models


class Migration(migrations.Migration):
    def dummy_reverse_code(app, schema_editor):
        pass

    dependencies = [
        ("common", "0018_update_aimmo_character_image_path"),
    ]

    operations = [
        migrations.RunPython(
            load_data_from_file("aimmo_characters3.json"),
            reverse_code=dummy_reverse_code,
        )
    ]
