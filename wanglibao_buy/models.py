# encoding:utf-8
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class TradeInfo(models.Model):
    type = models.CharField(help_text=u'产品种类', max_length=64)
    trade_type = models.CharField(help_text=u'交易类型（申购，购买，赎回）', max_length=16, blank=True)
    item_id = models.IntegerField(help_text=u'产品id')
    item_name = models.CharField(help_text=u'产品名称', blank=True, max_length=64)
    amount = models.IntegerField(help_text=u'金额（元）', default=0)
    user = models.ForeignKey(get_user_model())
    verify_info = models.CharField(help_text=u'验证消息，可以用来与购买放进行验证的编号（比如，数米的申请编号）', blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, help_text=u'购买发生时间', blank=True)
    related_info = models.TextField(blank=True, help_text=u'相关信息 csv')

    def __unicode__(self):
        return u'%s买了%s %s %d元' % (self.user.wanglibaouserprofile.phone, self.type, self.item_name, self.amount)


class FundHoldInfo(models.Model):
    user = models.ForeignKey(get_user_model())
    trade_account = models.CharField(help_text=u'用户数米交易账户', max_length=20)
    fund_code = models.CharField(help_text=u'基金代码', max_length=10)
    fund_name = models.CharField(help_text=u'基金名称', max_length=100)
    share_type = models.CharField(help_text=u'收费方式', max_length=10)
    current_remain_share = models.DecimalField(help_text=u'当前份额余额',  max_digits=20, decimal_places=2)
    usable_remain_share = models.DecimalField(help_text=u'可用份额余额',  max_digits=20, decimal_places=2)
    freeze_remain_share = models.DecimalField(help_text=u'冻结份额余额', max_digits=20, decimal_places=2)
    melon_method = models.CharField(help_text=u'分红方式', max_length=10)
    t_freeze_remain_share = models.DecimalField(help_text=u'交易冻结份额', max_digits=20, decimal_places=2)
    expire_shares = models.DecimalField(help_text=u'到期可用余额',  max_digits=20, decimal_places=2)
    unpaid_income = models.DecimalField(help_text=u'未付收益',  max_digits=20, decimal_places=2)
    pernet_value = models.DecimalField(help_text=u'单位净值',  max_digits=20, decimal_places=2)
    market_value = models.DecimalField(help_text=u'基金市值',  max_digits=20, decimal_places=3)
    nav_date = models.DateField(help_text=u'净值日期')
    bank_account = models.CharField(help_text=u'银行帐号', max_length=20)
    bank_name = models.CharField(help_text=u'银行名称', max_length=20)
    bank_serial = models.CharField(help_text=u'银行编号', max_length=10)
    fund_type = models.CharField(help_text=u'基金类型', max_length=10)
    fund_type_to_cn = models.CharField(help_text=u'基金类型名称', max_length=20)
    rapid_redeem = models.BooleanField(help_text=u'是否支持快速赎回')
    capital_mode = models.CharField(help_text=u'资金类型', max_length=10)
    create_date = models.DateField(help_text=u'持仓更新时间', auto_now=True)

    def __unicode__(self):
        return u'用户%s 持仓 %s: %s 余额<%s>' % (self.user, self.fund_code, self.fund_name, self.current_remain_share)
