# encoding: utf-8
#from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from wanglibao_p2p.models import P2PRecord


USER_TYPE = (
    ('0', u'正常用户'),
    ('1', u'渠道用户'),
    ('2', u'经纪人'),
    ('3', u'企业用户')
)


class WanglibaoUserProfile(models.Model):
    # user = models.OneToOneField(get_user_model(), primary_key=True)
    user = models.OneToOneField(User, primary_key=True)

    frozen = models.BooleanField(u'冻结状态', default=False)
    nick_name = models.CharField(max_length=32, blank=True, help_text=u'昵称')

    phone = models.CharField(max_length=64, blank=True, help_text=u'手机号码')
    phone_verified = models.BooleanField(default=False, help_text=u'手机号码是否已验证')

    name = models.CharField(max_length=12, blank=True, help_text=u'姓名')
    id_number = models.CharField(max_length=64, blank=True, help_text=u'身份证号', db_index=True)
    id_is_valid = models.BooleanField(help_text=u'身份证是否通过验证', default=False)
    id_valid_time = models.DateTimeField(blank=True, null=True, verbose_name=u"实名认证时间")

    shumi_request_token = models.CharField(max_length=64, blank=True, help_text=u'数米基金request token')
    shumi_request_token_secret = models.CharField(max_length=64, blank=True, help_text=u'数米基金request token secret')
    shumi_access_token = models.CharField(max_length=64, blank=True, help_text=u'数米基金access token')
    shumi_access_token_secret = models.CharField(max_length=64, blank=True, help_text=u'数米基金access token secret')

    risk_level = models.PositiveIntegerField(help_text=u'用户的风险等级', default=2)
    investment_asset = models.IntegerField(help_text=u'可投资额度(万)', default=30)
    investment_period = models.IntegerField(help_text=u'可投资期限(月)', default=3)

    deposit_default_bank_name = models.CharField(u'默认充值银行', max_length=32, blank=True)

    utype = models.CharField(u'用户类型', max_length=10, default='0', choices=USER_TYPE)

    gesture_pwd = models.CharField(u'手势密码', max_length=9, default='', blank=True)
    gesture_is_enabled = models.BooleanField(u'手势密码是否启用', default=False)

    trade_pwd = models.CharField(u'交易密码', max_length=128, default='', blank=True)
    trade_pwd_failed_count = models.IntegerField(help_text=u'交易密码连续输入错误次数', default=0)
    trade_pwd_last_failed_time = models.IntegerField(help_text=u'交易密码最后一次输入失败的时间',default=0)

    first_bind_time = models.IntegerField(u'第一次绑定微信时间', default=0)

    def __unicode__(self):
        return "phone: %s nickname: %s  %s" % (self.phone, self.nick_name, self.user.username)

    @property
    def is_invested(self):
        is_invested = False
        if P2PRecord.objects.filter(user=self.user, catalog=u'申购').count():
            is_invested = True
        return is_invested


class EnterpriseUserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    company_name = models.CharField(u'公司名称', max_length=30)
    business_license = models.ImageField(u'营业执照', upload_to='enterprise/license')
    registration_cert = models.ImageField(u'税务登记证', upload_to='enterprise/certificate')
    certigier_name = models.CharField(u'授权人姓名', max_length=12)
    certigier_phone = models.IntegerField(u'授权人手机号', max_length=64)
    company_address = models.TextField(u'公司地址', max_length=255)
    company_account = models.CharField(u'公司账户账号', max_length=64)
    company_account_name = models.CharField(u'公司账户名称', max_length=30)
    deposit_bank_province = models.CharField(u'公司开户行所在省份', max_length=10)
    deposit_bank_city = models.CharField(u'公司开户行所在市县', max_length=10)
    bank_branch_address = models.CharField(u'开户行支行所在地', max_length=100)
    modify_time = models.DateTimeField(u'最近修改时间', auto_now_add=True)
    created_time = models.DateTimeField(u'创建时间', auto_now=True)


def create_profile(sender, **kw):
    """
    Create the user profile when a user object is created
    """
    user = kw["instance"]
    if kw["created"]:
        profile = WanglibaoUserProfile(user=user)
        profile.save()

# post_save.connect(create_profile, sender=get_user_model(), dispatch_uid="users-profile-creation-signal")
post_save.connect(create_profile, sender=User, dispatch_uid="users-profile-creation-signal")
