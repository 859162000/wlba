# encoding: utf-8

#from __future__ import unicode_literals

from django.db import models

STATUS = (
    ("0", "监控中"),
    ("1", "正常用户"),
    ("2", "作弊用户"),
    ("3", "误击用户"),
)

class AntiDelayCallback(models.Model):
    uid = models.IntegerField()
    createtime = models.IntegerField()
    updatetime = models.IntegerField()
    channel = models.CharField(max_length=32, verbose_name='渠道标号')
    status = models.IntegerField(verbose_name='状态', choices=STATUS)
    device = models.CharField(max_length=1024)
    ip = models.CharField(max_length=32, verbose_name='IP地址')

    class Meta:
        verbose_name = u"渠道反作弊表"
        verbose_name_plural = u'渠道反作弊表'

    def __unicode__(self):
        return u"反作弊"

