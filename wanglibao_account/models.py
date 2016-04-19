#!/usr/bin/env python
# encoding: utf8

from django.contrib.auth.models import User
from django.db import models
from marketing.models import Channels


class Binding(models.Model):
    """
        third app bind table, store bind related
    """
    user = models.ForeignKey(User, related_name='binding')
    channel = models.ForeignKey(Channels, verbose_name=u"渠道", related_name='binding')
    bid = models.CharField(u"第三方用户id", max_length=50, db_index=True, blank=True)
    b_account = models.CharField(u"第三方用户账号", max_length=50, blank=True)
    extra = models.CharField(max_length=200, default="", blank=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    detect_callback = models.BooleanField(u"回调检测", default=False)

    class Meta:
        verbose_name = u'渠道用户绑定关系'
        verbose_name_plural = u'渠道用户绑定关系'
