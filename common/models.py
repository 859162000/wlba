#!/usr/bin/env python
# encoding: utf8

from django.contrib.auth.models import User
from django.db import models


class CallbackRecord(models.Model):
    REQUEST_ACT_CHOICE = (
        ('GET', 'GET'),
        ('POST', 'POST'),
    )

    user = models.ForeignKey(User)
    callback_to = models.CharField(u'回调渠道', max_length=30, db_index=True)
    order_id = models.CharField(u'关联订单号', max_length=50, db_index=True)
    third_order_id = models.CharField(u'渠道关联订单号', max_length=50, db_index=True, blank=True, null=True)
    result_code = models.CharField(u'渠道受理结果编码', max_length=30, blank=True, null=True)
    result_msg = models.CharField(u'渠道受理结果消息', max_length=255, blank=True, null=True)
    result_errors = models.TextField(u'渠道受理结果错误描述', max_length=500, blank=True, null=True)
    description = models.TextField(u'回调描述', max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    answer_at = models.DateTimeField(u'订单受理时间', blank=True, null=True)
    request_url = models.CharField(u'回调URL', max_length=255, blank=True, null=True)
    request_data = models.TextField(u'请求数据体', max_length=1000, blank=True, null=True)
    request_headers = models.TextField(u'请求数据头部', max_length=255, blank=True, null=True)
    request_action = models.CharField(u'请求动作', max_length=6, default=1, choices=REQUEST_ACT_CHOICE)
    ret_parser = models.CharField(u'回调结果解析器', max_length=50, blank=True, null=True)
    extra = models.CharField(max_length=200, default="", blank=True)
    re_callback = models.BooleanField(u"回调补发", default=False, help_text=u'如选择回调补发，则其他改动将不保存')

    class Meta:
        verbose_name = u'渠道回调记录'
        verbose_name_plural = u'渠道回调记录'
        unique_together = (("callback_to", "order_id"),)
