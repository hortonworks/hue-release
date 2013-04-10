# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management.base import NoArgsCommand
from useradmin.conf import DEFAULT_USERNAME, DEFAULT_USER_PASSWORD
from useradmin.forms import SuperUserChangeForm
from useradmin.models import get_default_user_group
from useradmin.views import ensure_home_directory
from hadoop import cluster


class Command(NoArgsCommand):

  def handle_noargs(self, **options):
    try:
      User.objects.get(username=DEFAULT_USERNAME.get())
    except User.DoesNotExist:
        fs = cluster.get_hdfs()
        form = SuperUserChangeForm(
            {
                "username": DEFAULT_USERNAME.get(),
                "password1": DEFAULT_USER_PASSWORD.get(),
                "password2": DEFAULT_USER_PASSWORD.get(),
                "ensure_home_directory": True,
                "is_active": True,
                "is_superuser": True,
                "groups": [get_default_user_group().pk]
            }
        )
        instance = form.save()
        ensure_home_directory(fs, instance.username)
