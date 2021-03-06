# encoding: utf-8
#from django.contrib.auth import get_user_model
import simplejson
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
    trade_pwd_last_failed_time = models.IntegerField(help_text=u'交易密码最后一次输入失败的时间', default=0)

    login_failed_count = models.IntegerField(u"登录失败次数", default=0)
    login_failed_time = models.DateTimeField(u'登录错误时间', auto_now_add=True, null=True)

    first_bind_time = models.IntegerField(u'第一次绑定微信时间', default=0)

    def __unicode__(self):
        return "phone: %s nickname: %s  %s" % (self.phone, self.nick_name, self.user.username)

    @property
    def is_invested(self):
        is_invested = False
        if P2PRecord.objects.filter(user=self.user, catalog=u'申购').count():
            is_invested = True
        return is_invested


def create_profile(sender, **kw):
    """
    Create the user profile when a user object is created
    """
    user = kw["instance"]
    if kw["created"]:
        profile = WanglibaoUserProfile(user=user)
        profile.save()

import decimal
from datetime import date, datetime
class Account2015(models.Model):
    user_id = models.IntegerField(primary_key=True)
    zc_ranking = models.IntegerField(u'注册排名', default=0, null=False)
    tz_times = models.IntegerField(u'投资次数', default=0, null=False)
    tz_amount = models.DecimalField(u'投资总金额', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_ranking_percent = models.DecimalField(u'投资排名百分比', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_max_amount = models.DecimalField(u'最大单笔投资额', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_max_ranking_percent = models.DecimalField(u'最大单笔投资排名百分比', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_sterm_amount = models.DecimalField(u'短期项目投资比例', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_mterm_amount = models.DecimalField(u'中期项目投资比例', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_lterm_amount = models.DecimalField(u'长期项目投资比例', default=0.00, null=False, max_digits=20, decimal_places=2)
    income_total = models.DecimalField(u'总收益', default=0.00, null=False, max_digits=20, decimal_places=2)
    income_reward = models.DecimalField(u'羊毛数', default=0.00, null=False, max_digits=20, decimal_places=2)
    income_hb_expire = models.DecimalField(u'过期红包金额', default=0.00, null=False, max_digits=20, decimal_places=2)
    income_jxq_expire = models.DecimalField(u'过期加息券额度', default=0.00, null=False, max_digits=20, decimal_places=2)
    invite_count = models.IntegerField(u'邀请好友数', default=0, null=False)
    invite_income = models.DecimalField(u'邀请好友总佣金', default=0.00, null=False, max_digits=20, decimal_places=2)

    first_visit_time = models.DateTimeField(u'首次访问时间', null=True)
    first_visit_ipaddr = models.CharField(u'首次访问来源IP地址', null=True, max_length=20)
    last_visit_time = models.DateTimeField(u'最近访问时间', null=True)
    last_visit_ipaddr = models.CharField(u'最近访问来源IP地址', null=True, max_length=20)
    total_visit_count = models.IntegerField(u'总计访问次数', default=0, null=False, db_index=True)

    def toJSON_filter(self, jsondump=False, include=None, exclude=None):
        fields = []
        for field in self._meta.fields:
            inflag = False
            if include:
                if field.name in include:
                   inflag = True
            else:
                inflag = True

            if exclude:
                if field.name in exclude:
                    inflag = False

            if inflag:
                fields.append(field.name)

        d = {}
        for attr in fields:
            value = getattr(self, attr)
            if isinstance(value, datetime):
                d[attr] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, date):
                d[attr] = value.strftime('%Y-%m-%d')
            elif isinstance(value, decimal.Decimal):
                d[attr] = str(value)
            else:
                d[attr] = getattr(self, attr)

        if jsondump:
            import json
            return json.dumps(d)
        else:
            return d


def save_to_redis(sender, **kw):
    """
    when userprofile saved, update the user info in redis.
    """
    from wanglibao_margin.php_utils import PhpRedisBackend
    user_profile = kw["instance"]
    user = user_profile.user
    redis_obj = PhpRedisBackend()
    redis_keys = redis_obj.redis.keys(pattern='python_{}_*'.format(user.pk))
    try:
        data = simplejson.loads(redis_obj.redis.get(redis_keys[0]))
        data.update(
            user_id=user.pk,
            username=user_profile.phone,
            realname=user.name,
            is_disable=user_profile.frozen,
            is_realname=1 if user_profile.id_is_valid else 0,
            is_admin=user.is_superuser,
            id_number=user.wanglibaouserprofile.id_number
        )
        for redis_key in redis_keys:
            redis_obj.redis.set(redis_key, simplejson.dumps(data))
    except Exception, e:
        print e
        for key in redis_keys:
            redis_obj.redis.delete(key)


# post_save.connect(create_profile, sender=get_user_model(), dispatch_uid="users-profile-creation-signal")
post_save.connect(create_profile, sender=User, dispatch_uid="users-profile-creation-signal")
post_save.connect(save_to_redis, sender=WanglibaoUserProfile, dispatch_uid="users-profile-save_to_redis-signal")

import decimal
from datetime import date, datetime
class Account2015(models.Model):
    user_id = models.IntegerField(primary_key=True)
    zc_ranking = models.IntegerField(u'注册排名', default=0, null=False)
    tz_times = models.IntegerField(u'投资次数', default=0, null=False)
    tz_amount = models.DecimalField(u'投资总金额', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_ranking_percent = models.DecimalField(u'投资排名百分比', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_max_amount = models.DecimalField(u'最大单笔投资额', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_max_ranking_percent = models.DecimalField(u'最大单笔投资排名百分比', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_sterm_amount = models.DecimalField(u'短期项目投资比例', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_mterm_amount = models.DecimalField(u'中期项目投资比例', default=0.00, null=False, max_digits=20, decimal_places=2)
    tz_lterm_amount = models.DecimalField(u'长期项目投资比例', default=0.00, null=False, max_digits=20, decimal_places=2)
    income_total = models.DecimalField(u'总收益', default=0.00, null=False, max_digits=20, decimal_places=2)
    income_reward = models.DecimalField(u'羊毛数', default=0.00, null=False, max_digits=20, decimal_places=2)
    income_hb_expire = models.DecimalField(u'过期红包金额', default=0.00, null=False, max_digits=20, decimal_places=2)
    income_jxq_expire = models.DecimalField(u'过期加息券额度', default=0.00, null=False, max_digits=20, decimal_places=2)
    invite_count = models.IntegerField(u'邀请好友数', default=0, null=False)
    invite_income = models.DecimalField(u'邀请好友总佣金', default=0.00, null=False, max_digits=20, decimal_places=2)

    first_visit_time = models.DateTimeField(u'首次访问时间', null=True)
    first_visit_ipaddr = models.CharField(u'首次访问来源IP地址', null=True, max_length=20)
    last_visit_time = models.DateTimeField(u'最近访问时间', null=True)
    last_visit_ipaddr = models.CharField(u'最近访问来源IP地址', null=True, max_length=20)
    total_visit_count = models.IntegerField(u'总计访问次数', default=0, null=False, db_index=True)

    def toJSON_filter(self, jsondump=False, include=None, exclude=None):
        fields = []
        for field in self._meta.fields:
            inflag = False
            if include:
                if field.name in include:
                   inflag = True
            else:
                inflag = True

            if exclude:
                if field.name in exclude:
                    inflag = False

            if inflag:
                fields.append(field.name)

        d = {}
        for attr in fields:
            value = getattr(self, attr)
            if isinstance(value, datetime):
                d[attr] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, date):
                d[attr] = value.strftime('%Y-%m-%d')
            elif isinstance(value, decimal.Decimal):
                d[attr] = str(value)
            else:
                d[attr] = getattr(self, attr)

        if jsondump:
            import json
            return json.dumps(d)
        else:
            return d


class ActivityUserInfo(models.Model):
    name = models.CharField(u'姓名', max_length=32)
    phone = models.CharField(u'手机号', max_length=11)
    address = models.TextField(u'地址', max_length=255)
    is_wlb_phone = models.BooleanField(u'是否网利宝手机号', default=False)
    extra = models.CharField(max_length=200, default="", blank=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(u'更新时间', auto_now=True)

    class Meta:
        verbose_name = u'活动用户信息'
        verbose_name_plural = u'活动用户信息'


class RepeatPaymentUser(models.Model):
    """3.31重复回款用户应收本息余额表"""
    user_id = models.IntegerField(u'用户ID', primary_key=True)
    name = models.CharField(u'姓名', max_length=32)
    phone = models.CharField(u'手机号', max_length=11)
    principal = models.DecimalField(u'应收本金', max_digits=10, decimal_places=2)
    interest = models.DecimalField(u'应收利息', max_digits=10, decimal_places=2)
    amount = models.DecimalField(u'剩余应收本息合计', max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'))
    is_every_day = models.BooleanField(u'是否每天自动扣款', default=True)
    product_ids = models.CharField(u'新投资标的ID', max_length=32, blank=True,
                                   help_text=u'如果用户不同意从每天的回款中扣除,则在此填写用户新购标的ID号,多个用,分割')

    class Meta:
        verbose_name = u'应收重复回款用户列表'
        verbose_name_plural = u'应收重复回款用户列表'


class RepeatPaymentUserRecords(models.Model):
    """重复回款用户应收本息扣款流水记录"""
    user_id = models.IntegerField(u'用户ID')
    name = models.CharField(u'姓名', max_length=32)
    phone = models.CharField(u'手机号', max_length=11)
    amount = models.DecimalField(u'扣款金额', max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'))
    amount_current = models.DecimalField(u'扣款后剩余应收', max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'))
    description = models.CharField(u'扣款描述', max_length=200, default=u'')
    create_time = models.DateTimeField(u'流水时间', auto_now_add=True)

    class Meta:
        verbose_name = u'应收重复回款用户扣款流水'
        verbose_name_plural = u'应收重复回款用户扣款流水'
