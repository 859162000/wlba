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

class InviteRelation(models.Model):
    user = models.ForeignKey(User)
    inviter = models.ForeignKey(User)
    activity_code = models.CharField(u'活动代码*', max_length=64, null=True)

class InviteUserExtraInfo(models.Model):
    user = models.ForeignKey(User)
    base_experience = models.FloatField(null=False, default=0, verbose_name=u'体验金金额')


class InviteRewardRecord(models.Model):
    invite_relation = models.ForeignKey(InviteRelation)
    reward_type = models.CharField()

# class




