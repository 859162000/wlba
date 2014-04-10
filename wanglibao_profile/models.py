# encoding: utf-8
from django.contrib.auth import get_user_model
from django.db import models


class WanglibaoUserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)

    nick_name = models.CharField(max_length=32, blank=True, help_text=u'昵称')

    phone = models.CharField(max_length=64, blank=True, help_text=u'手机号码')
    phone_verified = models.BooleanField(default=False, help_text=u'手机号码是否已验证')

    risk_level = models.PositiveIntegerField(help_text=u'用户的风险等级', default=2)
    investment_asset = models.IntegerField(help_text=u'可投资额度(万)', default=30)
    investment_period = models.IntegerField(help_text=u'可投资期限(月)', default=3)

    def __unicode__(self):
        return "%s phone: %s" % (self.user.username, self.phone)
