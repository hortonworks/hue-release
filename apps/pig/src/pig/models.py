## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.

from datetime import date
from django.db import models

from django.contrib.auth.models import User


class PigScript(models.Model):

    title = models.CharField('Title', max_length=200)
    pig_script = models.TextField('Pig script', null=True, blank=True)
    user = models.ForeignKey(User)
    python_script = models.TextField(null=True,blank=True)
    date_created = models.DateTimeField('Date', auto_now_add=True, auto_now=True)
    saved = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return u'%s' % self.title


class UDF(models.Model):
    url = models.CharField(max_length=255)
    file_name = models.CharField(max_length=55)
    description = models.TextField()
    owner = models.ForeignKey(User, verbose_name='Owner')

    class Meta:
        ordering = ['file_name']

    def __unicode__(self):
        return u'%s' % self.file_name


class Job(models.Model):
    JOB_SUBMITED = 1
    JOB_COMPLETED = 2

    JOB_STATUSES = (
        (JOB_SUBMITED, "Submited"),
        (JOB_COMPLETED, "Complited"),
        (3, "Failed"),
    )
    start_time = models.DateTimeField(auto_now_add=True)
    job_id = models.CharField(max_length=50, primary_key=True)
    statusdir = models.CharField(max_length=100)
    script = models.ForeignKey(PigScript)
    status = models.SmallIntegerField(choices=JOB_STATUSES, default=1)
    email_notification = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s" % self.job_id
