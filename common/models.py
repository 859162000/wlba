#!/usr/bin/env python
# encoding: utf8

from django.contrib.auth.models import User
from django.db import models


class CallbackRecord(models.Model):
    user = models.ForeignKey(User)
    callback_to = models.CharField(u'回调渠道', max_length=30, db_index=True)
    order_id = models.CharField(u'关联订单号', max_length=50, db_index=True)
    third_order_id = models.CharField(u'渠道关联订单号', max_length=50, blank=True, null=True)
    result_code = models.CharField(u'渠道受理结果编码', max_length=30, blank=True, null=True)
    result_msg = models.CharField(u'渠道受理结果消息', max_length=255, blank=True, null=True)
    description = models.TextField(u'回调描述', max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    answer_at = models.DateTimeField(u'订单受理时间', blank=True, null=True)

    class Meta:
        verbose_name = u'渠道回调记录'
        verbose_name_plural = u'渠道回调记录'
        unique_together = (("callback_to", "order_id"),)
