#encoding: utf-8
import datetime
from django.db import models
from django.utils import timezone
from wanglibao.models import ProductBase


class FundIssuer(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(default='')
    home_page = models.URLField(blank=True, default='')
    phone = models.CharField(max_length=64, default='')
    logo = models.ImageField(upload_to='bank_logo', null=True, blank=True, help_text=u'发行方图标')
    uuid = models.CharField(help_text=u'invest advisor guid', max_length=50, default='' )

    def __unicode__(self):
        return u'%s' % (self.name, )


class Fund(ProductBase):
    brief = models.TextField(blank=True, help_text=u"基金点评")

    name = models.CharField(max_length=64, help_text=u'基金名称')
    full_name = models.CharField(max_length=64, blank=True, help_text=u'基金全名')
    product_code = models.CharField(max_length=64, help_text=u'基金代码')
    type = models.CharField(max_length=16, blank=True, help_text=u'基金类型')
    invest_risk = models.CharField(max_length=16, blank=True, help_text=u'投资风险')
    status = models.CharField(max_length=16, blank=True, help_text=u'基金状态')
    trade_status = models.CharField(max_length=32, blank=True, help_text=u'交易状态')
    issuer = models.ForeignKey(FundIssuer)
    manager = models.TextField(help_text=u"基金经理")
    management_fee = models.FloatField(default=0, help_text=u'基金管理费')
    hosting_fee = models.FloatField(default=0, help_text=u'基金托管费')
    found_date = models.DateField(blank=True, null=True, help_text=u'成立日期')
    latest_shares = models.TextField(blank=True, help_text=u'最新份额 xxx.xx万份 (年-月-日)')
    init_scale = models.TextField(blank=True, help_text=u'首募规模 x.xx亿')
    latest_scale = models.TextField(blank=True, help_text=u'最新规模 x.xx亿 (年-月-日)')
    hosting_bank = models.CharField(max_length=32, blank=True, help_text=u'托管银行')
    investment_threshold = models.IntegerField(default=0, help_text=u'起投金额(元)')
    investment_target = models.TextField(blank=True, help_text=u'投资方向')
    investment_scope = models.TextField(blank=True, help_text=u'投资范围')
    investment_strategy = models.TextField(blank=True, help_text=u'投资策略')
    profit_allocation = models.TextField(blank=True, help_text=u'收益分配')
    risk_character = models.TextField(blank=True, help_text=u'风险收益特征')

    face_value = models.FloatField(default=0, help_text=u'净值')
    accumulated_face_value = models.FloatField(default=0, help_text=u'累计净值')
    rate_today = models.FloatField(default=0, help_text=u'当日收益率(非年化)')
    earned_per_10k = models.FloatField(default=0, help_text=u'万元收益')
    rate_7_days = models.FloatField(default=0, help_text=u'7日年化增长率')
    rate_1_week = models.FloatField(default=0, help_text=u'一周收益率')
    rate_1_month = models.FloatField(default=0, help_text=u'一月收益率')
    rate_3_months = models.FloatField(default=0, help_text=u'三月收益率')
    rate_6_months = models.FloatField(default=0, help_text=u'半年收益率')
    rate_1_year = models.FloatField(default=0, help_text=u'今年收益率(非年化)')
    profit_month = models.FloatField(default=0, help_text=u"当月收益")

    added = models.DateTimeField(default=timezone.now, help_text=u'加入系统时间')

    def __unicode__(self):
        return u'%s' % (self.name, )


class ChargeRate(models.Model):
    bottom_line = models.FloatField(default=0, help_text=u"下限")
    top_line = models.FloatField(default=0, help_text=u"上限")
    line_type = models.CharField(max_length=8, help_text=u"上下限值类型", choices=(
        (u'万元', u'万元'),
        (u'年', u'年'),
    ))

    value = models.FloatField(default=0, help_text=u'数值')
    value_type = models.CharField(default='percent', max_length=8, help_text=u"数值还是百分比", choices=(
        ('percent', u'百分比'),
        ('amount', u'数额'),
    ))

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