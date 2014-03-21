# encoding:utf-8
import datetime
from django.db import models


class Bank(models.Model):
    name = models.CharField(max_length=128, help_text=u'名字')
    phone = models.CharField(max_length=32, help_text=u'电话')
    description = models.TextField(blank=True, help_text=u'银行描述')
    home_url = models.URLField(help_text=u'主页链接')
    logo = models.ImageField(upload_to='bank_logo', null=True, blank=True, help_text=u'银行图标 用于理财产品的展示')

    def __unicode__(self):
        return u"%s" % (self.name,)


class BankFinancing(models.Model):
    name = models.CharField(max_length=128, help_text=u'名字')
    brief = models.TextField(blank=True, null=True, help_text=u'产品点评')
    expected_rate = models.FloatField(default=0, help_text=u'预期收益')
    period = models.IntegerField(default=0, help_text=u"产品管理期限 (天)")
    status = models.CharField(max_length=8, default=u'在售', help_text=u'销售状态')
    bank = models.ForeignKey(Bank)
    issue_target = models.CharField(max_length=16, default=u'个人', help_text=u'发行对象')
    currency = models.CharField(default=u'人民币', max_length=32, help_text=u'货币币种')
    investment_type = models.CharField(max_length=16, blank=True, help_text=u'投资类型')
    issue_start_date = models.DateField(blank=True, null=True, help_text=u'发行开始日期')
    issue_end_date = models.DateField(blank=True, null=True, help_text=u'发行结束日期')
    investment_threshold = models.FloatField(default=0, help_text=u'委托币种起始金额 (元)')
    investment_step = models.FloatField(default=0, help_text=u'起购金额递增单位')
    pledgable = models.BooleanField(default=False, help_text=u'可否质押贷款')
    bank_pre_redeemable = models.BooleanField(default=True, help_text=u'银行是否可提前终止')
    client_redeemable = models.BooleanField(default=True, help_text=u'客户是否可赎回')
    region = models.TextField(blank=True, help_text=u'销售地区')
    profit_type = models.CharField(max_length=32, help_text=u'收益类型')
    principle_guaranteed = models.BooleanField(default=False, help_text=u'是否保本')
    max_expected_profit_rate = models.FloatField(default=0, help_text=u'最大期待收益率')
    max_profit_rate = models.FloatField(default=0, help_text=u'到期最高收益')
    rate_compare_to_saving = models.FloatField(default=0, help_text=u'与同期储蓄比')
    profit_start_date = models.DateField(blank=True, null=True, help_text=u'收益开始日期')
    profit_end_date = models.DateField(blank=True, null=True, help_text=u'收益结束日期')

    risk_level = models.CharField(max_length=16, blank=True, help_text=u'风险评级')
    liquidity_level = models.CharField(max_length=16, blank=True, help_text=u'流动性评级')

    profit_description = models.TextField(blank=True, help_text=u'收益说明')
    buy_description = models.TextField(blank=True, help_text=u'申购条件说明')
    bank_pre_redeem_description = models.TextField(blank=True, help_text=u'银行提前终止条件')
    redeem_description = models.TextField(blank=True, help_text=u'赎回规定说明')
    risk_description = models.TextField(blank=True, help_text=u'投资风险说明')

    added = models.DateTimeField(default=datetime.datetime.now, help_text=u'添加时间')

    def __unicode__(self):
        return u"%s" % (self.name,)