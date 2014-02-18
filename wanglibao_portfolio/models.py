# This Python file uses the following encoding: utf-8
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models


class ProductType(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    average_earning_rate = models.FloatField(help_text="The average earning rate", default=0)
    average_risk_score = models.SmallIntegerField(default=0, help_text="The risk score for this type of product")

    def __unicode__(self):
        return '%s risk: %d rate: %.1f%%' % (self.name, self.average_risk_score, self.average_earning_rate)


class Portfolio(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()

    risk_score = models.SmallIntegerField(default=2, help_text="The risk score, it can be 1 to 5, 1 no risk, 5 crazy")
    asset_min = models.FloatField(help_text="The bottom line this portfolio applied")
    asset_max = models.FloatField(help_text="The top line this portfolio applied")

    period_min = models.FloatField(help_text="The minimum period", default=0)
    period_max = models.FloatField(help_text="The maximum period", default=0)

    investment_preference = models.CharField(max_length=16, help_text="Investment preference", default=u'平衡型')

    expected_earning_rate = models.FloatField(help_text="The expected earning rate for this portfolio")

    def __unicode__(self):
        return "%s risk:%d rate:%.1f" % (self.name, self.risk_score, self.expected_earning_rate)


class PortfolioProductEntry(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name="products")
    product = models.ForeignKey(ProductType)

    value = models.FloatField(help_text="How much of this product, 20000 or 10")
    type = models.CharField(max_length=16, default="percent",
                            choices=(('percent', 'percent'),
                                     ('amount', 'amount')),
                            help_text="Whether the value is percent or absolute value")
    description = models.TextField(help_text="Some description")

    def __unicode__(self):
        return '%s: %.2f %s' % (self.product.name, self.value, self.type)


class UserPortfolio(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)
    portfolio = models.ManyToManyField(Portfolio)
    created_at = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return u"%s portfolio:%s" % (self.user.username, '|'.join([unicode(p) for p in self.portfolio.all()]))
