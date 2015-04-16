from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

class Event(models.Model):
    dstamp = models.DateTimeField()
    app = models.CharField(max_length=100)
    user = models.ForeignKey(User, null=True)
    session = models.CharField(max_length=100, null=True)
    event_type = models.CharField(max_length=100)
    details = models.CharField(max_length=1000, null=True)

class HitsPerLevelPerDay(models.Model):
    date = models.DateField()
    level = models.CharField(max_length=1000, null=False)
    hits = models.IntegerField(null=False)
    updated_dstamp = models.DateTimeField(auto_now=False)
