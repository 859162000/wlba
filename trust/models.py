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
    english_name = models.TextField()

    registered_capital = models.IntegerField(verbose_name="registered capital in W")

    legal_presentative = models.TextField()
    chairman_of_board = models.TextField()
    manager = models.TextField()

    founded_at = models.DateField()
    appear_on_market = models.BooleanField()
    geo_region = models.TextField()

    shareholder_background = models.TextField()
    major_stockholder = models.TextField()
    shareholders = models.TextField()

    note = models.TextField() # Some note on the company

    business_range = models.TextField()

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
