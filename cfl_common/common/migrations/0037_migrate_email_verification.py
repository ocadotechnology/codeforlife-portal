from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0036_rename_awaiting_email_verification_userprofile_is_verified"),
    ]

    def forwards(apps, schema_editor):
        EmailVerification = apps.get_model("common", "EmailVerification")
        UserProfile = apps.get_model("common", "UserProfile")
        db_alias = schema_editor.connection.alias
        for email_verification in EmailVerification.objects.using(db_alias).filter(verified=True):
            UserProfile.objects.using(db_alias).filter(user=email_verification.user).update(is_verified=True)

    operations = [migrations.RunPython(forwards)]
