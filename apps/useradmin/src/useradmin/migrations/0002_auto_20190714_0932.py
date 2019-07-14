# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-14 09:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useradmin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='useradmin.OrganizationGroup', verbose_name='groups'),
        ),
    ]
