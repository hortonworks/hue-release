from datetime import date

from django.db import models
from profile.models import Profile


class PigScript(models.Model):

    title = models.CharField(max_length=200, verbose_name='Title')
    text = models.TextField(blank=True, verbose_name='Text')
    creater = models.ForeignKey(Profile, verbose_name='User')
    date_created = models.DateField(verbose_name='Date', auto_now_add=True)
    is_temporery = models.BooleanField(default=False,
                                       verbose_name='Is Temporery')
    pig_script = models.FileField(
        upload_to='pig_script/{t}'.format(t=date.today().isoformat()),
        verbose_name='Script file')

    class Meta:
        ordering = ['-date_created']

    def __unicode__(self):
        return u'%s' % self.title


class Jobs(models.Model):

    key = models.CharField(max_length=200, verbose_name='Key')
    value = models.CharField(max_length=200, verbose_name='Value')
