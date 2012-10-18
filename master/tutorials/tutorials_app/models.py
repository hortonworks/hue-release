from django.db import models
from django.contrib.auth.models import User


class Section(models.Model):
    order = models.IntegerField(max_length=2)
    lesson_name = models.CharField(max_length=30)
    add_time = models.IntegerField(max_length=20)

    def __str__(self):
        return str(self.order)


class Step(models.Model):
    order = models.IntegerField(max_length=2)
    file_path = models.CharField(max_length=255)
    add_time = models.IntegerField()
    section = models.ForeignKey(Section)

    def __str__(self):
        return "%s : %s" % (self.section, str(self.order))


class UserLocation(models.Model):
    step = models.ForeignKey(Step, null=True)
    user = models.ForeignKey(User)
    hue_location = models.CharField(max_length=512)


class UserStep(models.Model):
    step = models.ForeignKey(Step, null=True)
    user = models.ForeignKey(User)
    
