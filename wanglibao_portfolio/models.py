from django.contrib.auth import get_user_model
from django.db import models


class Portfolio(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()

    risk_score = models.SmallIntegerField(default=2, help_text="The risk score, it can be 1 to 5, 1 no risk, 5 crazy")
    asset_min = models.FloatField(help_text="The bottom line this portfolio applied")
    asset_max = models.FloatField(help_text="The top line this portfolio applied")

    expected_earning_rate = models.FloatField(help_text="The expected earning rate for this portfolio")

    cash = models.FloatField(help_text="The percent of cash", default=0)
    stock = models.FloatField(help_text="The percent of stock", default=0)
    p2p = models.FloatField(help_text="The percent of p2p", default=0)

    def __unicode__(self):
        return "%s risk:%d rate:%f" % (self.name, self.risk_score, self.expected_earning_rate)


class UserPortfolio(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)
    portfolio = models.ManyToManyField(Portfolio)

    def __unicode__(self):
        return u"%s portfolio:%s" % (self.user.username, '|'.join([unicode(p) for p in self.portfolio.all()]))
