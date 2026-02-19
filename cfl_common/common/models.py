from codeforlife.user.models import (
    Class,
    DailyActivity,
    JoinReleaseStudent,
    School,
    SchoolTeacherInvitation,
    Student,
    Teacher,
    TotalActivity,
    UserProfile,
    UserSession,
)

from django.db import models
import re


def stripStudentName(name):
    return re.sub("[ \t]+", " ", name.strip())

class DynamicElement(models.Model):
    """
    This model is meant to allow us to quickly update some elements
    dynamically on the website without having to redeploy everytime. For
    example, if a maintenance banner needs to be added, we check the box in
    the Django admin panel, edit the text and it'll show immediately on the
    website.
    """

    name = models.CharField(max_length=64, unique=True, editable=False)
    active = models.BooleanField(default=False)
    text = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name
