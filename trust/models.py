# encoding: utf-8
from requests import ConnectionError
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import ModelSerializer
from django.db import models
import logging

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

    note = models.TextField(blank=True, null=True) # Some note on the company

    business_range = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='trust_logo', null=True, blank=True, help_text=u'信托公司logo')

    def __unicode__(self):
        return self.name


class Trust (models.Model):
    name = models.TextField()
    short_name = models.CharField(max_length=256)
    expected_earning_rate = models.FloatField()
    brief = models.TextField()
    issuer = models.ForeignKey(Issuer, verbose_name="the issuer of this trust")
    available_region = models.TextField()
    scale = models.IntegerField(verbose_name="the scale of this trust, in the unit of RMB")

    investment_threshold = models.FloatField(verbose_name="the investment threshold in 10k")
    period = models.FloatField(verbose_name="the period in months")
    issue_date = models.DateField()
    type = models.TextField(verbose_name="trust type")

    earning_description = models.TextField()
    note = models.TextField(verbose_name="note on this trust")
    usage = models.CharField(max_length=100, verbose_name=u'用途')
    usage_description = models.TextField(u'用途描述')

    risk_management = models.TextField()
    mortgage = models.TextField(blank=True, help_text=u'抵押物')
    mortgage_rate = models.FloatField(default=0, help_text=u'抵押率')
    consignee = models.TextField(blank=True, help_text=u'受托人')
    payment = models.TextField(blank=True, help_text=u'支付情况')

    product_name = models.TextField()
    product_description = models.TextField(blank=True)
    related_info = models.TextField()

    def __unicode__(self):
        return self.name
