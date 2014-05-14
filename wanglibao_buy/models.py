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


class BindBank(models.Model):
    user = models.ForeignKey(get_user_model())
    no = models.CharField(help_text=u'银行卡号', max_length=20)
    balance = models.DecimalField(help_text=u'当前剩余限额', max_digits=20, decimal_places=2)
    bank_name = models.CharField(help_text=u'银行名称', max_length=20)
    bind_way = models.IntegerField(help_text=u'绑定方式')
    capital_mode = models.CharField(help_text=u'资金方式', max_length=20)
    content_describe = models.CharField(help_text=u'内容描述', max_length=500)
    is_freeze = models.BooleanField(help_text=u'是否冻结')
    is_vaild = models.BooleanField(help_text=u'是否经过验证')
    limit_describe = models.CharField(help_text=u'限额描述', max_length=200)
    priority = models.CharField(help_text=u'', max_length=20)
    status = models.CharField(help_text=u'当前银行卡状态', max_length=10)
    status_to_cn = models.CharField(help_text=u'当前银行卡状态说明', max_length=20)
    sub_trade_account = models.CharField(help_text=u'交易子帐号', max_length=20)
    support_auto_pay = models.BooleanField(help_text=u'是否支持自动交易')
    trade_account = models.CharField(help_text=u'交易帐号', max_length=20)
    create_date = models.DateField(help_text=u'创建时间', auto_now=True)

    def __unicode__(self):
        return u'% : %' % (self.bank_name, self.no)


class AvailableFund(models.Model):
    declare_status = models.BooleanField(help_text=u'申购状态')
    fund_code = models.CharField(help_text=u'基金代码', max_length=10)
    fund_name = models.CharField(help_text=u'基金名称', max_length=100)
    fund_state = models.CharField(help_text=u'基金状态', max_length=10)
    fund_type = models.CharField(help_text=u'基金类型', max_length=10)
    last_update = models.CharField(help_text=u'更新时间', max_length=20)
    min_shares = models.DecimalField(help_text=u'最低持有份额', max_digits=20, decimal_places=2)
    purchase_limit_max = models.DecimalField(help_text=u'申购最大限额', max_digits=20, decimal_places=2)
    purchase_limit_min = models.DecimalField(help_text=u'申购最小限额', max_digits=20, decimal_places=2)
    purchase_second_limit_min = models.DecimalField(help_text=u'二次申购最小份额', max_digits=20, decimal_places=2)
    quick_cash_limit_max = models.DecimalField(help_text=u'快速取现最大限额', max_digits=20, decimal_places=2)
    quick_cash_limit_min = models.DecimalField(help_text=u'快速取现最小限额', max_digits=20, decimal_places=2)
    ration_limit_max = models.DecimalField(help_text=u'定投协议最大限额', max_digits=20, decimal_places=2)
    ration_limit_min = models.DecimalField(help_text=u'定投协议最小限额', max_digits=20, decimal_places=2)
    redeem_limit_max = models.DecimalField(help_text=u'赎回最大限额', max_digits=20, decimal_places=2)
    redeem_limit_min = models.DecimalField(help_text=u'赎回最小限额', max_digits=20, decimal_places=2)
    risk_level = models.IntegerField(help_text=u'基金风险级别')
    share_type = models.CharField(help_text=u'收费方式', max_length=10)
    subscribe_limit_max = models.DecimalField(help_text=u'认购最大限额', max_digits=20, decimal_places=2)
    subscribe_limit_min = models.DecimalField(help_text=u'认购最小份额', max_digits=20, decimal_places=2)
    subscribe_state = models.BooleanField(help_text=u'认购状态')
    transform_limit_max = models.DecimalField(help_text=u'转换最大限额', max_digits=20, decimal_places=2)
    transform_limit_min = models.DecimalField(help_text=u'转换最小限额', max_digits=20, decimal_places=2)
    valuagr_state = models.BooleanField(help_text=u'定投状态')
    withdraw_state = models.BooleanField(help_text=u'赎回状态')
    create_date = models.DateField(help_text=u'创建时间', auto_now=True)

    def __unicode__(self):
        return u'<%s: %s> %s' % (self.fund_code, self.fund_name, self.fund_type)


class TradeHistory(models.Model):
    user = models.ForeignKey(get_user_model())
    amount = models.DecimalField(help_text=u'数量', max_digits=20, decimal_places=2)
    apply_date_time = models.DateField(help_text=u'发生时间')
    apply_serial = models.CharField(help_text=u'流水号', max_length=50)
    bank_account = models.CharField(help_text=u'银行卡号', max_length=20)
    bank_name = models.CharField(help_text=u'银行名称', max_length=20)
    bank_serial = models.CharField(help_text=u'银行编号', max_length=10)
    business_type = models.CharField(help_text=u'业务类型', max_length=10)
    business_type_to_cn = models.CharField(help_text=u'业务类型描述', max_length=100)
    can_cancel = models.BooleanField(help_text=u'是否可撤销')
    fund_code = models.CharField(help_text=u'基金代码', max_length=10)
    fund_name = models.CharField(help_text=u'基金名称', max_length=100)
    is_cash_buy = models.BooleanField(help_text=u'是否现金宝')
    pay_result = models.IntegerField(help_text=u'支付结果')
    pay_status_to_cn = models.CharField(help_text=u'支付状态描述', max_length=50)
    pound_age = models.DecimalField(help_text=u'手续费', max_digits=20, decimal_places=2)
    share_type = models.CharField(help_text=u'收费方式', max_length=10)
    share_type_to_cn = models.CharField(help_text=u'收费方式描述', max_length=20)
    shares = models.DecimalField(help_text=u'申请份额', max_digits=20, decimal_places=2)
    status = models.IntegerField(help_text=u'订单状态')
    status_to_cn = models.CharField(help_text=u'订单状态描述', max_length=100)
    trade_account = models.CharField(help_text=u'交易帐号', max_length=20)
    create_date = models.DateField(help_text=u'创建时间')

    def __unicode__(self):
        return u'流水号: %s ,用户 %s %s <%s: %s> 数量 %s' % (self.apply_serial, self.user,
                                                           self.business_type_to_cn, self.fund_code,
                                                           self.fund_name, self.amount)

