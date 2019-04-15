from django.contrib.auth.models import User
from django.utils import timezone


def get_superuser():
    """Get a superuser for testing, or create one if there isn't one."""
    try:
        return User.objects.get(username="superuser")
    except User.DoesNotExist:
        return User.objects.create_superuser(
            "superuser", "superuser@codeforlife.education", "password"
        )


def create_user_directly(active=True, **kwargs):
    """Create a inactive user on the database."""
    days_to_subtract = 10 if active else 2000
    username = "old_user+{:d}".format(create_user_directly.next_id)
    user = User.objects.create_user(username, password="password")
    user.last_login = timezone.now() - timezone.timedelta(days=days_to_subtract)
    user.date_joined = timezone.now() - timezone.timedelta(days=days_to_subtract - 1)
    user.save()

    create_user_directly.next_id += 1


create_user_directly.next_id = 1
