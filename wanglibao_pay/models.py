#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from order.models import Order
from wanglibao_margin.models import MarginRecord
from wanglibao_pay.util import get_a_uuid


class Bank(models.Model):
    name = models.CharField(verbose_name=u'银行', max_length=32)
    gate_id = models.CharField(max_length=8, verbose_name=u'gate id')
    code = models.CharField(max_length=16, verbose_name=u'银行代码')
    limit = models.TextField(blank=True, verbose_name=u'汇付网银银行限额信息')
    logo = models.ImageField(upload_to='bank_logo', null=True, blank=True, help_text=u'银行图标')
    sort_order = models.IntegerField(default=0, verbose_name=u'排序权值 从大到小')
    kuai_code = models.CharField(max_length=16, verbose_name=u'快钱侧银行代码', null=True, blank=True)
    #银行限额信息格式如下,"|"分隔第一次和第二次
    #单笔=5000,单日=5000|单笔=50000,单日=10000000
    kuai_limit = models.CharField(max_length=500, blank=True, verbose_name=u'快钱侧银行限额信息')
    huifu_bind_limit = models.CharField(max_length=500, blank=True, verbose_name=u"汇付快捷限额信息", default="")
    huifu_bind_code = models.CharField(max_length=20, verbose_name=u'汇付侧银行代码', blank=True, default="")
    yee_bind_limit = models.CharField(max_length=500, blank=True, verbose_name=u"易宝快捷限额信息", default="")
    yee_bind_code = models.CharField(max_length=20, verbose_name=u'易宝侧银行代码', blank=True, default="")

    #last_update = models.DateTimeField(u'更新时间', auto_now=True, null=True)

    channel = models.CharField(u'支付通道', max_length=20, blank=True, null=True, choices=(
        ("huifu", "Huifu"),
        ("yeepay", "Yeepay"),
        ("kuaipay", "Kuaipay")
    ))

    class Meta:
        ordering = '-sort_order',
        verbose_name_plural = "银行"

    def __unicode__(self):
        return u'%s' % self.name

    @classmethod
    def get_deposit_banks(cls):
        return Bank.objects.all().exclude(gate_id='').exclude(gate_id__isnull=True).select_related()

    @classmethod
    def get_withdraw_banks(cls):
        return Bank.objects.all().exclude(code='').exclude(code__isnull=True).select_related()

    @classmethod
    def get_kuai_deposit_banks(cls):
        return Bank.objects.all().exclude(kuai_code='').exclude(kuai_code__isnull=True).select_related()

    @classmethod
    def get_bind_channel_banks(cls):
        return Bank.objects.all().exclude(channel__isnull=True).exclude(kuai_code__isnull=True).exclude(huifu_bind_code__isnull=True).exclude(yee_bind_code__isnull=True).select_related()

class Card(models.Model):
    no = models.CharField(max_length=25, verbose_name=u'卡号')
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    user = models.ForeignKey(User)
    is_default = models.BooleanField(verbose_name=u'是否为默认', default=False)
    add_at = models.DateTimeField(auto_now=True)
    is_bind_huifu = models.BooleanField(verbose_name=u"是否绑定汇付快捷", default=False)
    is_bind_kuai = models.BooleanField(verbose_name=u"是否绑定快钱快捷", default=False)
    is_bind_yee = models.BooleanField(verbose_name=u"是否绑定易宝快捷", default=False)
    last_update = models.DateTimeField(u'更新时间', auto_now=True, null=True)
    yee_bind_id = models.CharField(max_length=50, verbose_name=u'易宝帮卡id', blank=True, default="")

    class Meta:
        verbose_name_plural = "银行卡"

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

    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'支付记录'

    type = models.CharField(u'类型', help_text=u'充值：D 取款：W', max_length=5)
    uuid = models.CharField(u'唯一标示', max_length=32, unique=True, db_index=True, default=get_a_uuid)
    amount = models.DecimalField(u'实扣金额', max_digits=20, decimal_places=2)
    fee = models.DecimalField(u'手续费', max_digits=20, decimal_places=2, default=0)
    total_amount = models.DecimalField(u'总金额', max_digits=20, decimal_places=2, default=0)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)
    confirm_time = models.DateTimeField(u'审核时间', blank=True, null=True)
    request = models.TextField(u'请求数据', blank=True)
    response = models.TextField(u'返回数据', blank=True)
    status = models.CharField(u'状态', max_length=15)
    error_code = models.CharField(u'错误码', max_length=10, blank=True)
    error_message = models.CharField(u'错误原因', max_length=100, blank=True)
    request_ip = models.CharField(u'请求地址', max_length=50, blank=True, null=True)
    response_ip = models.CharField(u'响应地址', max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, blank=True, null=True)
    margin_record = models.ForeignKey(MarginRecord, blank=True, null=True)
    bank = models.ForeignKey(Bank, blank=True, null=True, on_delete=models.PROTECT, verbose_name=u'银行')
    account_name = models.CharField(u'姓名', max_length=12, blank=True, null=True)
    card_no = models.CharField(u'卡号', max_length=25, blank=True, null=True)
    channel = models.CharField(u'支付通道', max_length=20, blank=True, null=True, choices=(
        ("huifu", "Huifu"), #汇付网银
        ("huifu_bind", "Huifu_bind"), #汇付快捷
        ("yeepay", "Yeepay"), #易宝
        ("yeepay_bind", "Yeepay_bind"), #易宝快捷
        ("app", "App"), #app取现使用
        ("kuaipay", "Kuaipay") #快钱
    ))

    def __unicode__(self):
        return u'%s' % self.pk

    def toJSON(self):
        import simplejson
        return simplejson.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))


class PayResult(object):
    DEPOSIT_SUCCESS = u'充值成功'
    DEPOSIT_FAIL = u'充值失败'
    WITHDRAW_SUCCESS = u'提现成功'
    WITHDRAW_FAIL = u'提现失败'
    RETRY = u'系统内部错误，请重试'
    EXCEPTION = u'系统内部错误，请联系客服'
