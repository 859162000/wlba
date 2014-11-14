#!/usr/bin/env python
# encoding:utf-8

import time
from django.db import models

class Misc(models.Model):
    key = models.CharField(u'键', max_length=50)
    value = models.CharField(u'值(可存json.dumps后的数据)', max_length=1000)
    description = models.CharField(u'描述', max_length=200, blank=True, default="")
    stype = models.CharField(u'类型', max_length=20, blank=True, default="")
    created_at = models.BigIntegerField(default=long(time.time()), verbose_name=u"创建时间", blank=True)
    updated_at = models.BigIntegerField(default=long(time.time()), verbose_name=u"更新时间", blank=True)

    class Meta:
        verbose_name_plural = u"杂项配置表"
