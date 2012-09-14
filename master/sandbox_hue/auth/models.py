from django.db import models
from django.contrib.auth.models import User, UserManager
from auth.fields import AutoOneToOneField

class UserProfile(User):
	phone = models.CharField(max_length=20)
	user = AutoOneToOneField(User, related_name='profile', verbose_name=('User'), primary_key=True)

class Section(models.Model):
	name = models.CharField(max_length = 50)
	order = models.IntegerField(max_length = 2)
	description = models.TextField()
	section_level = models.IntegerField(max_length = 1)
	section_user_type = models.IntegerField(max_length = 1)
	lesson_name = models.CharField(max_length = 30)
	add_time = models.TimeField()

class Step(models.Model):
	name = models.CharField(max_length = 50)
	description = models.TextField()
	video_url = models.CharField(max_length = 50)
	order = models.IntegerField(max_length = 2)
	help_text = models.TextField()
	add_time = models.TimeField()
	section = models.ForeignKey(Section)

class UserStep(models.Model):
	step = models.ForeignKey(Step)
	user = models.ForeignKey(UserProfile)
	status = models.IntegerField(max_length = 1)

class StepSave(models.Model):
	user_step = models.ForeignKey(UserStep)
	note = models.CharField(max_length = 255)


