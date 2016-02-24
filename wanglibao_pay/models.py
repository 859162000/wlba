#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from order.models import Order
from wanglibao_margin.models import MarginRecord
from wanglibao_pay.util import get_a_uuid
from wanglibao_pay import util
from decimal import Decimal


class Bank(models.Model):
    name = models.CharField(verbose_name=u'银行', max_length=32)
    gate_id = models.CharField(max_length=8, unique=True, verbose_name=u'gate id')
    code = models.CharField(max_length=16, verbose_name=u'银行代码')
    limit = models.TextField(blank=True, verbose_name=u'汇付网银银行限额信息')
    logo = models.ImageField(upload_to='bank_logo', null=True, blank=True, help_text=u'银行图标')
    sort_order = models.IntegerField(default=0, verbose_name=u'排序权值 从大到小')
    kuai_code = models.CharField(max_length=16, verbose_name=u'快钱侧银行代码', null=True, blank=True)
    # 银行限额信息格式如下,"|"分隔第一次和第二次
    # 单笔=5000,单日=5000|单笔=50000,单日=10000000
    kuai_limit = models.CharField(max_length=500, blank=True, verbose_name=u'快钱侧银行限额信息')
    huifu_bind_limit = models.CharField(max_length=500, blank=True, verbose_name=u"汇付快捷限额信息", default="")
    huifu_bind_code = models.CharField(max_length=20, verbose_name=u'汇付侧银行代码', blank=True, default="")
    yee_bind_limit = models.CharField(max_length=500, blank=True, verbose_name=u"易宝快捷限额信息", default="")
    yee_bind_code = models.CharField(max_length=20, verbose_name=u'易宝侧银行代码', blank=True, default="")
    # 提现限额:min_amount=50,max_amount=50000
    withdraw_limit = models.CharField(max_length=500, blank=True, verbose_name=u"银行提现限额", default="")
    have_company_channel = models.BooleanField(u"是否对公", default=False)

    #last_update = models.DateTimeField(u'更新时间', auto_now=True, null=True)

    channel = models.CharField(u'手机支付通道', max_length=20, blank=True, null=True, choices=(
        ("huifu", "Huifu"),
        ("yeepay", "Yeepay"),
        ("kuaipay", "Kuaipay")
    ))

    pc_channel = models.CharField(u'pc支付通道', max_length=20, default='huifu', blank=False, null=False, choices=(
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
        banks = Bank.objects.all().exclude(channel__isnull=True)\
            .exclude(kuai_code__isnull=True).exclude(huifu_bind_code__isnull=True)\
            .exclude(yee_bind_code__isnull=True).select_related()
        rs = []
        for bank in banks:
            obj = {"name": bank.name, "gate_id": bank.gate_id, "bank_id": bank.code, "bank_channel": bank.channel}
            if bank.channel == 'kuaipay' and bank.kuai_limit:
                obj.update(util.handle_kuai_bank_limit(bank.kuai_limit))
            elif bank.channel == 'huifu' and bank.huifu_bind_limit:
                obj.update(util.handle_kuai_bank_limit(bank.huifu_bind_limit))
            elif bank.channel == 'yeepay' and bank.yee_bind_limit:
                obj.update(util.handle_kuai_bank_limit(bank.yee_bind_limit))
            else:
                # 只返回已经有渠道的银行
                continue

            rs.append(obj)
        return rs

class Card(models.Model):
    no = models.CharField(max_length=25, verbose_name=u'卡号', db_index=True)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    user = models.ForeignKey(User)
    is_default = models.BooleanField(verbose_name=u'是否为默认', default=False)
    add_at = models.DateTimeField(auto_now_add=True)
    is_bind_huifu = models.BooleanField(verbose_name=u"是否绑定汇付快捷", default=False)
    is_bind_kuai = models.BooleanField(verbose_name=u"是否绑定快钱快捷", default=False)
    is_bind_yee = models.BooleanField(verbose_name=u"是否绑定易宝快捷", default=False)
    last_update = models.DateTimeField(u'更新时间', auto_now=True, null=True)
    yee_bind_id = models.CharField(max_length=50, verbose_name=u'易宝帮卡id', blank=True, default="")
    # 同卡进出
    is_the_one_card = models.BooleanField(verbose_name='是否为唯一进出卡片', default=False)

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

    DEPOSIT = 'D'  # 充值
    WITHDRAW = 'W'  # 提现

    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'支付记录'

    type = models.CharField(u'类型', help_text=u'充值：D 取款：W', max_length=5)
    uuid = models.CharField(u'唯一标示', max_length=32, unique=True, db_index=True, default=get_a_uuid)
    amount = models.DecimalField(u'实扣金额', max_digits=20, decimal_places=2)
    fee = models.DecimalField(u'手续费', max_digits=20, decimal_places=2, default=0)
    management_fee = models.DecimalField(u'资金管理费用', max_digits=20, decimal_places=2, default=0)
    management_amount = models.DecimalField(u'资金管理金额', max_digits=20, decimal_places=2, default=0)
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
    phone_for_card = models.CharField(u'预留手机号', max_length=25, blank=True, null=False, default='')
    channel = models.CharField(u'支付通道', max_length=20, blank=True, null=True, choices=(
        ("huifu", "Huifu"), #汇付网银
        ("huifu_bind", "Huifu_bind"), #汇付快捷
        ("yeepay", "Yeepay"), #易宝
        ("yeepay_bind", "Yeepay_bind"), #易宝快捷
        ("app", "App"), #app取现使用
        ("kuaipay", "Kuaipay") #快钱
    ))
    device = models.CharField(u'设备类型', max_length=20, blank=True, default='', choices=(
        ('pc', 'pc'),
        ('android', 'android'),
        ('ios', 'ios')
    ))

    def __unicode__(self):
        return u'%s' % self.pk

    def toJSON(self):
        import simplejson
        return simplejson.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))

    def save_error(self, error_code, error_message, is_inner_error=False):
        self.error_code = str(error_code)
        self.error_message = error_message
        if is_inner_error:
            self.status = self.EXCEPTION
        else:
            self.status = self.FAIL
        self.save()

    @property
    def total_fee(self):
        return self.fee + self.management_fee


class WithdrawCard(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    bank_name = models.CharField(max_length=64, verbose_name=u'开户行名称')
    card_name = models.CharField(max_length=64, verbose_name=u'银行户名')
    card_no = models.CharField(max_length=25, verbose_name=u'银行卡号')
    amount = models.DecimalField(verbose_name=u'账户余额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    freeze = models.DecimalField(verbose_name=u'冻结金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    is_default = models.BooleanField(verbose_name=u'是否为默认', default=True)

    class Meta:
        verbose_name_plural = u'公司提现账户'

    def __unicode__(self):
        return u'%s' % self.card_no


class WithdrawCardRecord(models.Model):
    type = models.CharField(u'类型', help_text=u'充值：D 取款：W', max_length=5)
    uuid = models.CharField(u'唯一标示', max_length=32, unique=True, db_index=True, default=get_a_uuid)
    amount = models.DecimalField(u'金额', max_digits=20, decimal_places=2)
    fee = models.DecimalField(u'手续费', max_digits=20, decimal_places=2, default=0)
    management_fee = models.DecimalField(u'资金管理费用', max_digits=20, decimal_places=2, default=0)
    management_amount = models.DecimalField(u'资金管理金额', max_digits=20, decimal_places=2, default=0)
    withdrawcard = models.ForeignKey(WithdrawCard, on_delete=models.PROTECT)
    payinfo = models.ForeignKey(PayInfo, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, blank=True, null=True)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)
    confirm_time = models.DateTimeField(u'审核时间', blank=True, null=True)
    status = models.CharField(u'状态', max_length=15)
    message = models.CharField(u'操作信息', max_length=100, blank=True)
    ip = models.CharField(u'操作IP', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = u'公司提现账户操作记录'


class PayResult(object):
    DEPOSIT_SUCCESS = u'充值成功'
    DEPOSIT_FAIL = u'充值失败'
    WITHDRAW_SUCCESS = u'提现成功'
    WITHDRAW_FAIL = u'提现失败'
    RETRY = u'系统内部错误，请重试'
    EXCEPTION = u'系统内部错误，请联系客服'


class WhiteListCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    card_no = models.CharField(max_length=25, verbose_name=u'银行卡号', db_index=True)
    create_time = models.DateTimeField(u'添加时间', auto_now_add=True, db_index=True)
    message = models.CharField(u'操作信息', max_length=100, blank=True)

    class Meta:
        verbose_name_plural = u'银行卡白名单'


class BlackListCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    card_no = models.CharField(max_length=25, verbose_name=u'银行卡号', db_index=True)
    create_time = models.DateTimeField(u'添加时间', auto_now_add=True, db_index=True)
    message = models.CharField(u'操作信息', max_length=100, blank=True)
    ip = models.CharField(u'IP地址', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = u'银行卡黑名单'
