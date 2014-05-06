# encoding: utf-8
from django.contrib.auth import get_user_model
from django.db import models


class WanglibaoUserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)

    nick_name = models.CharField(max_length=32, blank=True, help_text=u'昵称')

    phone = models.CharField(max_length=64, blank=True, help_text=u'手机号码')
    phone_verified = models.BooleanField(default=False, help_text=u'手机号码是否已验证')

    name = models.CharField(max_length=12, blank=True, help_text=u'姓名')
    id_number = models.CharField(max_length=64, blank=True, help_text=u'身份证号', db_index=True)

    shumi_request_token = models.CharField(max_length=64, blank=True, help_text=u'数米基金request token')
    shumi_request_token_secret = models.CharField(max_length=64, blank=True, help_text=u'数米基金request token secret')
    shumi_access_token = models.CharField(max_length=64, blank=True, help_text=u'数米基金access token')
    shumi_access_token_secret = models.CharField(max_length=64, blank=True, help_text=u'数米基金access token secret')

    risk_level = models.PositiveIntegerField(help_text=u'用户的风险等级', default=2)
    investment_asset = models.IntegerField(help_text=u'可投资额度(万)', default=30)
    investment_period = models.IntegerField(help_text=u'可投资期限(月)', default=3)

    def __unicode__(self):
        return "%s phone: %s" % (self.user.username, self.phone)
