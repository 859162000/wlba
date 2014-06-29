# coding=utf-8
from django.db import models


class NewsAndReport(models.Model):
    name = models.CharField(u'名字', max_length=128)
    link = models.URLField(u'链接', null=True)
    score = models.IntegerField(u'排名权重', default=0)
    created_at = models.DateTimeField(u'添加时间', auto_now_add=True)

    class Meta:
        ordering = ['-score']

    def __unicode__(self):
        return self.name

