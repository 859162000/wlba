# encoding: utf-8

#from __future__ import unicode_literals

from django.db import models

class AntiDelayCallback(models.Model):
    uid = models.IntegerField()
    createtime = models.IntegerField()
    updatetime = models.IntegerField()
    channel = models.CharField(max_length=32)
    status = models.IntegerField()
    device = models.CharField(max_length=1024)
    ip = models.CharField(max_length=32)

    def __unicode__(self):
        return u"反作弊"

