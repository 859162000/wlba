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

    face_value = models.FloatField()
    accumulated_face_value = models.FloatField()
    rate_day = models.FloatField()

    earned_per_10k = models.FloatField()
    profit_rate_7days = models.FloatField()
    profit_per_month = models.FloatField(help_text="Latest profilt per month")
    type = models.CharField(max_length=16, help_text="The type of fund, currency, debt, stock index etc")

    fund_date = models.DateField()
    sales_url = models.URLField()
    status = models.CharField(max_length=16)

    mode = models.CharField(max_length=16, help_text="qi yue xing kai fang shi")
    scale = models.FloatField(help_text="How large the fund is now")

    hosted_bank = models.CharField(max_length=64)
    hosted_bank_description = models.TextField()

    performance_compare_baseline = models.TextField()

    invest_target = models.TextField()
    invest_scope = models.TextField()

    manager = models.TextField()

    portfolio = models.TextField(help_text="Json data for current portfolio")

    management_charge_rate = models.FloatField()
    frontend_hosting_charge_rate = models.FloatField()

    buy_front_charge_rate = models.TextField(help_text="JSON")
    buy_back_charge_rate = models.TextField()

    sale_front_charge_rate = models.TextField()
    sale_back_charge_rate = models.TextField()

    def __unicode__(self):
        return u'%s' % (self.name, )