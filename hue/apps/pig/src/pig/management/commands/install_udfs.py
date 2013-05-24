# -*- coding: utf-8 -*-
import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from hadoop import cluster
from pig import conf
from pig.models import UDF
from useradmin.conf import DEFAULT_USERNAME
from useradmin.management.commands import create_sandbox_user

UDF_PATH = conf.UDF_PATH.get()


class Command(BaseCommand):

    args = '<udf1.jar udf2.jar ...>'
    help = 'Upload and register specific udfs. If no udfs presented, update udfs from hdfs.'

    def handle(self, *args, **options):
        fs = cluster.get_hdfs()
        fs.setuser(fs.DEFAULT_USER)
        if not fs.exists(UDF_PATH):
            fs.mkdir(UDF_PATH, 0777)

        for f in args:
          file_name = os.path.split(f)[-1]
          path = fs.join(UDF_PATH, file_name)
          fs.do_as_user(default_user.username, fs.copyFromLocal, f, path)
          UDF.objects.create(url=path, file_name=file_name, owner=default_user)
        if not args:
          for f in fs.listdir(UDF_PATH):
            try:
              UDF.objects.get(file_name=f)
            except UDF.DoesNotExist:
              path = fs.join(UDF_PATH, f)
              UDF.objects.create(url=path, file_name=f, owner=default_user)
