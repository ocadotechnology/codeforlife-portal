from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0036_rename_awaiting_email_verification_userprofile_is_verified"),
    ]

    def forwards(apps, schema_editor):
        """ Finds the users of verified Email Verification objects and sets their `is_verified` to True """
        EmailVerification = apps.get_model("common", "EmailVerification")
        UserProfile = apps.get_model("common", "UserProfile")
        db_alias = schema_editor.connection.alias
        for email_verification in EmailVerification.objects.using(db_alias).filter(verified=True):
            UserProfile.objects.using(db_alias).filter(user=email_verification.user).update(is_verified=True)

    def backwards(apps, schema_editor):
        """ Finds the users of verified Email Verification objects and sets their `is_verified` to False """
        EmailVerification = apps.get_model("common", "EmailVerification")
        UserProfile = apps.get_model("common", "UserProfile")
        db_alias = schema_editor.connection.alias
        for email_verification in EmailVerification.objects.using(db_alias).filter(verified=True):
            UserProfile.objects.using(db_alias).filter(user=email_verification.user).update(is_verified=False)

    operations = [migrations.RunPython(forwards, reverse_code=backwards)]
