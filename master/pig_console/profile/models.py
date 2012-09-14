# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User)
    public_profile_field = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s' % self.user.username


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
