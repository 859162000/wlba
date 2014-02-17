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

    earned_per_10k = models.FloatField(default=0)
    profit_rate_7days = models.FloatField(default=0)
    profit_rate_month = models.FloatField(default=0)
    profit_rate_3months = models.FloatField(default=0)
    profit_rate_6months = models.FloatField(default=0)
    profit_per_month = models.FloatField(help_text="Latest profilt per month")
    type = models.CharField(max_length=16, help_text="The type of fund, currency, debt, stock index etc")

    fund_date = models.DateField()
    sales_url = models.URLField()
    status = models.CharField(max_length=16)

    issuable = models.BooleanField(default=True)
    redeemable = models.BooleanField(default=True)
    AIP_able = models.BooleanField(default=True, help_text="Automatic Investment Plan")

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
