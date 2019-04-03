import datetime

from django.contrib.auth.models import User
from django.utils import timezone


def get_superuser():
    try:
        return User.objects.get(username="superuser")
    except:
        return User.objects.create_superuser(
            "superuser", "superuser@codeforlife.education", "password"
        )


def create_inactive_user_directly(**kwargs):
    username = "old_user+{:d}".format(create_inactive_user_directly.next_id)
    user = User.objects.create_user(username, password="password")
    user.last_login = timezone.now() - timezone.timedelta(days=2000)
    user.date_joined = timezone.now() - timezone.timedelta(days=2001)
    user.save()

    create_inactive_user_directly.next_id += 1
    return user, username, "password"


create_inactive_user_directly.next_id = 1
