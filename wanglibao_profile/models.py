from django.contrib.auth import get_user_model
from django.db import models


class WanglibaoUserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)

    phone = models.CharField(verbose_name="Mobile phone number", max_length=64, default="")
    phone_verified = models.BooleanField(verbose_name="Mobile phone verified", default=False)

    identity_type = models.CharField(verbose_name="Identity type: id, passport etc", max_length=10, default="id", choices=(
        ('id', 'id card number'),
        ('passport', 'passport number'),
        ('military', 'military id')
    ))
    identity = models.CharField(verbose_name="Identity", max_length=128, default="")

    risk_level = models.PositiveIntegerField(verbose_name="How risky the user is, 1..5", default=2)
    investment_asset = models.IntegerField(verbose_name="How many money", default=0)
    total_asset = models.IntegerField(verbose_name="Total asset", default=0)

    def __unicode__(self):
        return "%s phone: %s" % (self.user.username, self.phone)
