from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("common", "0006_update_aimmo_character_image_path")]

    operations = [migrations.RunPython(migrations.RunPython.noop, reverse_code=migrations.RunPython.noop)]
