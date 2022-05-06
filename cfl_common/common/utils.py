import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist
from two_factor.utils import default_device

from .models import Class, Student, Teacher


def two_factor_cache_key(user):
    """Cache key for using_two_factor."""
    return "using-two-factor-%s" % user.pk


def _using_two_factor(user):
    """Returns whether the user is using 2fa or not."""
    return default_device(user)


def using_two_factor(user):
    """Returns whether the user is using 2fa or not (Cached)."""
    if hasattr(user, "using_two_factor_cache"):
        # First try local memory, as we call this a lot in one request
        return user.using_two_factor_cache
    cache_key = two_factor_cache_key(user)
    val = cache.get(cache_key)
    if val is not None:
        # If local memory failed, but we got it from memcache, set local memory
        user.using_two_factor_cache = val
        return val
    val = bool(_using_two_factor(user))

    # We didn't find it in the cache, so set it there and local memory
    cache.set(cache_key, val, None)  # Cache forever
    user.using_two_factor_cache = val
    return val


def field_exists(model, field):
    try:
        field = model._meta.get_field(field)
    except FieldDoesNotExist:
        return False
    return True


def __anonymise_user(user: User):
    # the actual user anonymisation
    user.username = uuid.uuid4().hex
    user.first_name = "Deleted"
    user.last_name = "User"
    user.email = ""
    user.is_active = False
    user.save()


def anonymise(user: User):
    """Anonymise user. If admin teacher, pass the admin role to another teacher (if exists).
    If the only teacher, anonymise the school.
    """
    is_admin = False
    teacher = None
    teacher_set = Teacher.objects.filter(new_user=user)
    if teacher_set:
        is_admin = teacher_set[0].is_admin
        school = teacher_set[0].school
        teacher = teacher_set[0]

    __anonymise_user(user)

    # if teacher, anonymise classes and students
    if teacher:
        classes = Class.objects.filter(teacher=teacher)
        for klass in classes:
            students = Student.objects.filter(class_field=klass)
            for student in students:
                __anonymise_user(student.new_user)
            klass.anonymise()

    # if user is admin and the school does not have another admin, appoint another teacher as admin
    if is_admin:
        teachers = Teacher.objects.filter(school=school).order_by(
            "new_user__last_name", "new_user__first_name"
        )
        if not teachers:
            # no other teacher, anonymise the school
            school.anonymise()
            return

        admin_exists = False
        for teacher in teachers:
            if teacher.is_admin:
                admin_exists = True
                break

        # if no admin, appoint the first teacher as admin
        if not admin_exists:
            teachers[0].is_admin = True
            teachers[0].save()


class LoginRequiredNoErrorMixin(LoginRequiredMixin):
    """
    Overwrites Django's 2.2 LoginRequiredMixin so as to not raise an error and
    redirect instead.
    """

    def handle_no_permission(self):
        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name(),
        )
