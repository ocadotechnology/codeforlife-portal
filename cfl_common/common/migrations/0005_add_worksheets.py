from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("common", "0004_add_aimmocharacters")]

    operations = [migrations.RunPython(migrations.RunPython.noop, reverse_code=migrations.RunPython.noop)]
