#!/usr/bin/env python
# encoding:utf-8

from django.db import models
from ckeditor.fields import RichTextField


class Topic(models.Model):
    name = models.CharField(verbose_name=u'话题', max_length=50)

    class Meta:
        verbose_name_plural = '话题'

    def __unicode__(self):
        return u'%s' % self.name

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, verbose_name='话题')
    title = models.CharField(max_length=200, verbose_name=u'问题')
    answer = RichTextField()
    hotspot = models.BooleanField(default=False, verbose_name=u'是否是热点问题')
    sortord = models.IntegerField(default=0, verbose_name=u'排序值(大的排在前)')

    class Meta:
        verbose_name_plural = '问题'

    def __unicode__(self):
        return "%s" % self.title

