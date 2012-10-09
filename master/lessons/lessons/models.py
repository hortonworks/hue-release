from django.db import models
from django.contrib.auth.models import User, UserManager

from django.contrib import admin

class Section(models.Model):
    name = models.CharField(max_length = 50)
    order = models.IntegerField(max_length = 2)
    description = models.TextField()
    section_level = models.IntegerField(max_length = 1)
    section_user_type = models.IntegerField(max_length = 1)
    lesson_name = models.CharField(max_length = 30)
    add_time = models.IntegerField(max_length = 20)
    def __str__(self):
        return self.name

admin.site.register(Section)

class Step(models.Model):
    name = models.CharField(max_length = 50)
    order = models.IntegerField(max_length = 2)
    file_path = models.CharField(max_length=255)
    add_time = models.IntegerField()
    section = models.ForeignKey(Section)
    def __str__(self):
        return "%s : %s" % (self.section, self.name)

admin.site.register(Step)

class UserStep(models.Model):
    step = models.ForeignKey(Step)
    user = models.ForeignKey(User)
    status = models.IntegerField(max_length = 1)

admin.site.register(UserStep)

class StepSave(models.Model):
    user_step = models.ForeignKey(UserStep)
    note = models.CharField(max_length = 255)

admin.site.register(StepSave)


