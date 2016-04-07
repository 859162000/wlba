# encoding: utf-8
import collections
import logging
from decimal import Decimal
from datetime import datetime
import reversion
from concurrency.fields import IntegerVersionField
from django.db import models
from django.db.models import Sum, SET_NULL
from django.db.models.signals import post_save
from django.utils import timezone
from django.contrib.auth.models import User
from weixin.models import WeixinUser

REWARD_TYPE = (
    ('redpack', u'优惠券'),
    ('experience_gold', u'体验金'),
)

class InviteRelation(models.Model):
    user = models.ForeignKey(User)
    inviter = models.ForeignKey(User)
    activity_code = models.CharField(u'活动代码*', max_length=64, null=True)

class UserExtraInfo(models.Model):
    user = models.ForeignKey(User)
    invite_experience_amount = models.FloatField(null=False, default=0, verbose_name=u'体验金金额')


class InviteRewardRecord(models.Model):
    ACTION = (
        ('R', u'注册'),
        ('L', u'登录'),
        ('V', u'实名认证'),
        ('D', u'充值'),
        ('B', u'购买'),
        ('FB', u'首次购买'),
    )
    invite_relation = models.ForeignKey(InviteRelation)
    action = models.CharField(max_length=10, blank=False, null=False, choices=ACTION)
    reward_type = models.CharField(u'奖品类型', max_length=20, choices=REWARD_TYPE)
    redpack_record_id = models.IntegerField(default=0, verbose_name=u'优惠券发放流水ID', null=True)
    experience_gold_record_id = models.IntegerField(default=0, verbose_name=u'体验金发放流水ID', null=True)
    status = models.BooleanField(default=False, verbose_name=u'是否成功')
    created_at = models.DateTimeField(auto_now=True, default=timezone.now)


class WechatUserDailyReward(models.Model):
    ACTION_TYPES = (
        (u'redpack_rain', u'红包雨'),
    )
    w_user = models.ForeignKey(WeixinUser)
    user = models.ForeignKey(User, null=True)
    action_type = models.CharField(u'动作类型', choices=ACTION_TYPES, max_length=32)
    create_date = models.DateField(u'创建日期', auto_now_add=True,  db_index=True)
    reward_type = models.CharField(u'奖品类型', max_length=20, choices=REWARD_TYPE)
    redpack_id = models.IntegerField(default=0, verbose_name=u'优惠券ID', null=True)
    experience_gold_id = models.IntegerField(default=0, verbose_name=u'优惠券ID', null=True)
    redpack_record_id = models.IntegerField(default=0, verbose_name=u'体验金ID', null=True)
    experience_gold_record_id = models.IntegerField(default=0, verbose_name=u'体验金发放流水ID', null=True)
    desc = models.CharField(u'描述', max_length=64, null=True)
    status = models.BooleanField(default=False, verbose_name=u'是否成功')

    class Meta:
        unique_together = (("w_user", "create_date"),)  # 联合唯一索引








