import common.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0058_userprofile_google_refresh_token_and_more"),
        ("game", "0117_update_solutions_to_if_else"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL("""
ALTER TABLE auth_user RENAME TO user_user;
ALTER TABLE common_class RENAME TO user_class;
ALTER TABLE common_dailyactivity RENAME TO user_dailyactivity;
ALTER TABLE common_joinreleasestudent RENAME TO user_joinreleasestudent;
ALTER TABLE common_school RENAME TO user_school;
ALTER TABLE common_schoolteacherinvitation RENAME TO user_schoolteacherinvitation;
ALTER TABLE common_student RENAME TO user_student;
ALTER TABLE common_teacher RENAME TO user_teacher;
ALTER TABLE common_totalactivity RENAME TO user_totalactivity;
ALTER TABLE common_userprofile RENAME TO user_userprofile;
ALTER TABLE common_usersession RENAME TO user_usersession;
""")
            ],
            state_operations=[
                migrations.DeleteModel(name="Class"),
                migrations.DeleteModel(name="DailyActivity"),
                migrations.DeleteModel(name="JoinReleaseStudent"),
                migrations.DeleteModel(name="School"),
                migrations.DeleteModel(name="SchoolTeacherInvitation"),
                migrations.DeleteModel(name="Student"),
                migrations.DeleteModel(name="Teacher"),
                migrations.DeleteModel(name="TotalActivity"),
                migrations.DeleteModel(name="UserProfile"),
                migrations.DeleteModel(name="UserSession"),
            ]
        )
    ]
