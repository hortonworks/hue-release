from django.db import models
from django.contrib.auth.models import User

VERSION = 1

class UserLocation(models.Model):
    user = models.ForeignKey(User)
    step_location = models.CharField(max_length=512, null=True)
    hue_location = models.CharField(max_length=512)

