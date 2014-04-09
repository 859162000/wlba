# encoding: utf-8
from django.db import models


class CashIssuer(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    home_page = models.URLField()
    phone = models.CharField(max_length=64)
    logo = models.ImageField(upload_to='bank_logo', null=True, blank=True)

    def __unicode__(self):
        return u'%s' % (self.name, )


class Cash(models.Model):
    name = models.CharField(max_length=64)
    issuer = models.ForeignKey(CashIssuer)
    status = models.CharField(max_length=16)
    period = models.IntegerField()
    profit_rate_7days = models.FloatField(default=0)
    profit_10000 = models.FloatField(default=0)
    buy_url = models.URLField(max_length=1024, help_text=u'购买链接')
    buy_text = models.CharField(max_length=25)
    brief = models.TextField()
    buy_brief = models.TextField(blank=True, null=True)
    redeem_brief = models.TextField(blank=True, null=True)
    profit_brief = models.TextField(blank=True, null=True)
    safe_brief = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.name, )
