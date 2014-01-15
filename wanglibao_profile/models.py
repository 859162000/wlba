from django.db import models
from registration.models import User


class WanglibaoUserProfile(models.Model):
    user = models.ForeignKey(User, primary_key=True)
    risk_level = models.PositiveIntegerField(verbose_name="How risky the user is, 1..5", default=2)
    investment_asset = models.IntegerField(verbose_name="How many money", default=0)
    total_asset = models.IntegerField(verbose_name="Total asset", default=0)



