__author__ = 'lishuo'

from django.db import models

class Issuer(models.Model):
    name = models.TextField()
    short_name = models.TextField()
    english_name = models.TextField()

    registered_capital = models.IntegerField(verbose_name="Registered capital in W")

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
    issuer = models.ForeignKey(Issuer, verbose_name="The issuer of this trust")
    available_region = models.TextField()
    scale = models.IntegerField(verbose_name="The scale of this trust, in the unit of RMB")

    investment_threshold = models.FloatField(verbose_name="The investment threshold in 10k")
    period = models.FloatField(verbose_name="The period in months")
    issue_date = models.DateField()
    type = models.TextField(verbose_name="Trust type")

    earning_description = models.TextField()
    note = models.TextField(verbose_name="note on this trust")
    usage = models.CharField(max_length=100, verbose_name="usage", choices=(
        ('estate', 'estate'),
        ('finance', 'finance'),
        ('infrastructure', 'infrastructure'),
        ('others', 'others')
    ))
    usage_description = models.TextField()

    risk_management = models.TextField()
    payment = models.TextField()

    product_name = models.TextField()
    related_info = models.TextField()

    def __unicode__(self):
        return self.name




