# encoding: utf-8
from django.db import models
import logging
from wanglibao.models import ProductBase

logger = logging.getLogger(__name__)


class Issuer(models.Model):
    name = models.TextField()
    short_name = models.TextField()
    english_name = models.TextField(blank=True, null=True)

    registered_capital = models.IntegerField(blank=True, null=True, verbose_name="registered capital in W")

    legal_presentative = models.TextField(blank=True, null=True)
    chairman_of_board = models.TextField(blank=True, null=True)
    manager = models.TextField(blank=True, null=True)

    founded_at = models.DateField(blank=True, null=True)
    appear_on_market = models.BooleanField(blank=True)
    geo_region = models.TextField(blank=True, null=True)

    shareholder_background = models.TextField(blank=True, null=True)
    major_stockholder = models.TextField(blank=True, null=True)
    shareholders = models.TextField(blank=True, null=True)

    note = models.TextField(blank=True, null=True)

    business_range = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='trust_logo', null=True, blank=True, help_text=u'信托公司logo')

    def __unicode__(self):
        return self.name


class Trust (ProductBase):
    ON_SALE = u'在售'
    PRE_SALE = u'预售'
    EXPIRED = u'停售'
    PRODUCT_STATUS = (
        (ON_SALE, ON_SALE),
        (PRE_SALE, PRE_SALE),
        (EXPIRED, EXPIRED)
    )

    TYPES = (
        (u'信托', u'信托'),
        (u'有限合伙', u'有限合伙'),
        (u'资管', u'资管')
    )

    name = models.TextField(verbose_name=u'信托名称')
    short_name = models.CharField(max_length=256, verbose_name=u'短名称')
    status = models.CharField(max_length=10, verbose_name=u'销售状态', choices=PRODUCT_STATUS, default=ON_SALE, blank=True, null=True)
    expected_earning_rate = models.FloatField(verbose_name=u'预期收益')
    expected_earning_rate_high = models.FloatField(verbose_name=u'最高预期收益', default=0)
    product_type = models.CharField(max_length=20, verbose_name=u'产品类型', choices=TYPES, default=u'信托')
    brief = models.TextField(blank=True, null=True, verbose_name=u'点评')
    issuer = models.ForeignKey(Issuer, verbose_name=u"发行机构")
    available_region = models.TextField(blank=True, null=True, verbose_name=u'发行区域')
    scale = models.IntegerField(blank=True, null=True, verbose_name=u"发行规模(万元)")

    investment_threshold = models.FloatField(blank=True, null=True, verbose_name=u"投资限额（万元）")
    period = models.FloatField(blank=True, null=True, verbose_name=u"期限（月）")
    issue_date = models.DateField(blank=True, null=True, verbose_name=u'发行时间')
    type = models.TextField(blank=True, null=True, verbose_name=u"类型")

    earning_description = models.TextField(blank=True, null=True, verbose_name=u'收益说明')
    usage = models.CharField(blank=True, null=True, max_length=100, verbose_name=u'投资行业')
    usage_description = models.TextField(blank=True, null=True, verbose_name=u'用途描述')

    risk_management = models.TextField(blank=True, null=True, verbose_name=u'风险控制')
    mortgage = models.TextField(blank=True, verbose_name=u'抵押物')
    mortgage_rate = models.FloatField(default=0, verbose_name=u'抵押率')
    consignee = models.TextField(blank=True, verbose_name=u'受托人')
    payment = models.TextField(blank=True, verbose_name=u'支付情况')
    guarantee = models.TextField(blank=True, verbose_name=u'担保')
    financing_party = models.CharField(max_length=100, blank=True, verbose_name=u'融资方')
    financing_party_description = models.TextField(blank=True, verbose_name=u'融资方介绍')
    interest_method = models.CharField(max_length=25, blank=True, verbose_name=u'付息方式')
    source_of_repayment = models.TextField(blank=True, verbose_name=u'还款来源')

    product_description = models.TextField(blank=True, verbose_name=u'产品说明')
    related_info = models.TextField(blank=True, null=True, verbose_name=u'相关信息')

    def __unicode__(self):
        return self.name
