#encoding: utf-8
from django.db import models


class FundIssuer(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    home_page = models.URLField()
    phone = models.CharField(max_length=64)

    def __unicode__(self):
        return u'%s' % (self.name, )


class Fund(models.Model):
    name = models.CharField(max_length=64)
    full_name = models.CharField(max_length=64)
    product_code = models.CharField(max_length=64)
    issuer = models.ForeignKey(FundIssuer)
    brief = models.TextField(help_text="Some comments by gurus")
    currency = models.CharField(max_length=16, blank=True, help_text=u'货币')

    target_user = models.CharField(max_length=16, blank=True)
    available_region = models.TextField(blank=True, help_text=u'销售地区')

    invest_type = models.CharField(max_length=16, blank=True, default=u'保守型')

    face_value = models.FloatField()
    accumulated_face_value = models.FloatField()
    rate_day = models.FloatField()

    earned_per_10k = models.FloatField(default=0)
    profit_rate_7days = models.FloatField(default=0)
    profit_rate_month = models.FloatField(default=0)
    profit_rate_3months = models.FloatField(default=0)
    profit_rate_6months = models.FloatField(default=0, help_text=u'近六月收益率')
    profit_per_month = models.FloatField(help_text="当月收益")

    profit_description = models.TextField(default=u'--', help_text=u'收益说明')
    buy_description = models.TextField(default=u'--', help_text=u'申购条件说明')

    type = models.CharField(max_length=16, help_text=u"基金类型，货币，股指，qfii?")

    found_date = models.DateField(blank=True, null=True, help_text=u'成立日期')
    start_date = models.DateField(blank=True, null=True, help_text=u'开始日期')
    end_date = models.DateField(blank=True, null=True, help_text=u'结束日期')

    sales_url = models.URLField(blank=True, help_text=u'产品销售网址')
    status = models.CharField(max_length=16, help_text=u'基金状态')

    issuable = models.BooleanField(default=True, help_text=u'是否可发行')
    redeemable = models.BooleanField(default=True, help_text=u'是否可赎回')
    AIP_able = models.BooleanField(default=True, help_text=u'是否可定投')

    mode = models.CharField(max_length=16, help_text=u"基金模式")
    scale = models.FloatField(help_text=u"基金规模")

    hosted_bank = models.CharField(max_length=64, help_text=u'托管银行')
    hosted_bank_description = models.TextField(u'托管银行描述')

    performance_compare_baseline = models.TextField(u'收益对比基数')

    invest_target = models.TextField(help_text=u'投资方向')
    invest_scope = models.TextField(help_text=u'投资范围')

    manager = models.TextField(help_text=u"基金经理")

    portfolio = models.TextField(help_text=u"资产配置")

    management_charge_rate = models.FloatField()
    management_period = models.FloatField(default=0, help_text=u'委托管理期限')
    management_threshold = models.FloatField(default=0, help_text=u'委托管理起始资金')
    invest_step = models.FloatField(default=0, help_text=u'起购金额递增单位')

    pledgable = models.BooleanField(default=False, help_text=u'可否质押贷款')
    bank_redeemable = models.BooleanField(default=False, help_text=u'银行可否提前终止')
    bank_redeem_condition = models.TextField(blank=True, help_text=u'银行提前终止条件')
    client_redeemable = models.BooleanField(default=False, help_text=u'客户是否可赎回')
    client_redeem_description = models.TextField(blank=True, help_text=u'客户赎回规定说明')

    risk_description = models.TextField(blank=True, help_text=u'投资风险说明')

    frontend_hosting_charge_rate = models.FloatField(default=0, help_text=u'前端托管费率')

    def __unicode__(self):
        return u'%s' % (self.name, )


class ChargeRate(models.Model):
    bottom_line = models.FloatField(help_text="bottom line in 10K units")
    top_line = models.FloatField(help_text="top line in 10K unites")
    line_type = models.CharField(max_length=8, help_text="line value type, amount, year")

    value = models.FloatField()
    value_type = models.CharField(max_length=8, help_text="percent or amount")

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"%f - %f %s: %f %s" % (self.bottom_line, self.top_line, self.line_type, self.value, self.value_type)


class IssueFrontEndChargeRate(ChargeRate):
    fund = models.ForeignKey(Fund, related_name="issue_front_end_charge_rates")


class IssueBackEndChargeRate(ChargeRate):
    fund = models.ForeignKey(Fund, related_name="issue_back_end_charge_rates")


class RedeemFrontEndChargeRate(ChargeRate):
    fund = models.ForeignKey(Fund, related_name="redeem_front_end_charge_rates")


class RedeemBackEndChargeRate(ChargeRate):
    fund = models.ForeignKey(Fund, related_name="redeem_back_end_charge_rates")
