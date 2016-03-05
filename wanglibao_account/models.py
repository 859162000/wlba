#!/usr/bin/env python
# encoding: utf8

from django.contrib.auth.models import User
from django.db import models
from marketing.models import Channels


class UserThreeOrder(models.Model):
    user = models.ForeignKey(User)
    order_on = models.ForeignKey(Channels, verbose_name=u'订单渠道')
    third_order_id = models.CharField(u'渠道订单号', max_length=50, blank=True, null=True)
    request_no = models.CharField(unique=True, max_length=30, verbose_name=u'请求流水号')
    result_code = models.CharField(max_length=30, blank=True, verbose_name=u'受理结果编码')
    msg = models.CharField(max_length=255, blank=True, verbose_name=u'受理结果消息')
    created_at = models.DateTimeField(u'下单时间', auto_now_add=True)
    answer_at = models.DateTimeField(u'订单反馈时间', blank=True, null=True)

    class Meta:
        verbose_name_plural = u'渠道订单记录'


class Binding(models.Model):
    """
        third app bind table, store bind related
    """
    user = models.ForeignKey(User)
    channel = models.ForeignKey(Channels, verbose_name=u"渠道")
    bid = models.CharField(u"第三方用户id", max_length=50, db_index=True, blank=True)
    extra = models.CharField(max_length=200, default="", blank=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    detect_callback = models.BooleanField(u"回调检测", default=False)

    class Meta:
        verbose_name_plural = u'用户绑定'
