# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class PayInfo(models.Model):
    INITIAL = u'初始'
    PROCESSING = u'处理中'
    SUCCESS = u'成功'
    FAIL = u'失败'

    type = models.CharField(verbose_name=u'类型', help_text=u'充值：D 取款：W', max_length=5)
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=u'金额')
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    request = models.TextField(verbose_name=u'请求数据', blank=True)
    response = models.TextField(verbose_name=u'返回数据', blank=True)
    status = models.CharField(max_length=15, verbose_name=u'状态')
    error_code = models.CharField(max_length=10, verbose_name=u'错误码', blank=True)
    error_message = models.CharField(max_length=100, verbose_name=u'错误原因', blank=True)
    user = models.ForeignKey(get_user_model())
