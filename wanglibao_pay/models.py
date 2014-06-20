# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from order.models import Order
from wanglibao_buy.models import BindBank


class Bank(models.Model):
    name = models.CharField(verbose_name=u'银行', max_length=32)
    gate_id = models.CharField(max_length=8, verbose_name=u'gate id')
    code = models.CharField(max_length=16, verbose_name=u'银行代码')
    limit = models.TextField(blank=True, verbose_name=u'银行限额信息')
    logo = models.ImageField(upload_to='bank_logo', null=True, blank=True, help_text=u'银行图标')
    sort_order = models.IntegerField(default=0, verbose_name=u'排序权值 从大到小')

    class Meta:
        ordering = '-sort_order',

    def __unicode__(self):
        return u'%s' % self.name


class Card(models.Model):
    no = models.CharField(max_length=25, verbose_name=u'卡号')
    bank = models.ForeignKey(Bank)
    user = models.ForeignKey(get_user_model())
    is_default = models.BooleanField(verbose_name=u'是否为默认', default=False)

    def __unicode__(self):
        return u'%s' % self.no


class PayInfo(models.Model):
    INITIAL = u'初始'
    PROCESSING = u'处理中'
    SUCCESS = u'成功'
    FAIL = u'失败'
    EXCEPTION = u'异常'
    ACCEPTED = u'已受理'

    DEPOSIT = 'D'
    WITHDRAW = 'W'

    type = models.CharField(verbose_name=u'类型', help_text=u'充值：D 取款：W', max_length=5)
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=u'金额')
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    request = models.TextField(verbose_name=u'请求数据', blank=True)
    response = models.TextField(verbose_name=u'返回数据', blank=True)
    status = models.CharField(max_length=15, verbose_name=u'状态')
    error_code = models.CharField(max_length=10, verbose_name=u'错误码', blank=True)
    error_message = models.CharField(max_length=100, verbose_name=u'错误原因', blank=True)
    request_ip = models.CharField(max_length=50, verbose_name=u'请求地址', blank=True, null=True)
    response_ip = models.CharField(max_length=50, verbose_name=u'响应地址', blank=True, null=True)
    user = models.ForeignKey(get_user_model())
    card = models.ForeignKey(Card, blank=True, null=True)
    order = models.ForeignKey(Order, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.pk

