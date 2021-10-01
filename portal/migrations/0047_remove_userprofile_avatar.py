from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("portal", "0046_auto_20150723_1101")]

    operations = [migrations.RemoveField(model_name="userprofile", name="avatar")]
