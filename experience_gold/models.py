#!/usr/bin/env python
# encoding:utf-8

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
# import datetime


PLATFORM = (
    ("all", "全平台"),
    ("ios", "ios"),
    ("android", "android"),
    ("pc", "pc"),
    ("app", "移动端"),
)


class ExperienceProduct(models.Model):
    """ 体验标 """
    name = models.CharField(max_length=30, verbose_name=u'体验标名称')
    period = models.IntegerField(default=0, verbose_name=u'期限(天)', blank=False)
    expected_earning_rate = models.FloatField(default=0, verbose_name=u'年化收益(%)', blank=False)
    description = models.CharField(max_length=20, verbose_name=u"描述", default="")
    isvalid = models.BooleanField(default=False, verbose_name=u"是否有效")

    class Meta:
        verbose_name = u"体验标"
        verbose_name_plural = u"体验标"

    def __unicode__(self):
        return u'%s <%s>' % (self.id, self.name)


class ExperienceEvent(models.Model):
    """ 体验金活动 """
    name = models.CharField(max_length=30, verbose_name=u'体验金名称')
    amount = models.FloatField(null=False, default=0, verbose_name=u'体验金金额')
    description = models.CharField(max_length=20, verbose_name=u"描述", blank=True, default="")
    give_mode = models.CharField(max_length=20, verbose_name=u"发放方式", db_index=True, choices=(
        ("activity", u"活动奖励"),
        ("register", u"注册"),
        ("validation", u"实名认证"),
        ("first_buy", u"首次投资"),
        ("first_pay", u"首次充值"),
        ('buy', u'投资'),
        ('pay', u'充值'),
        ('p2p_audit', u'满标审核'),
        ('repaid', u'还款'),
        ('weixin_sign_in', u'微信签到'),
    ), default=u"注册")
    give_platform = models.CharField(max_length=10, verbose_name=u"发放平台", default=u"全平台", choices=PLATFORM)
    target_channel = models.CharField(max_length=1000, verbose_name=u"渠道", blank=True, default="",
                                      help_text=u'不限渠道则留空即可,多个渠道用英文逗号间隔')
    available_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"生效时间")
    unavailable_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"失效时间")
    invalid = models.BooleanField(default=False, verbose_name=u"是否作废")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta:
        verbose_name = u"体验金活动"
        verbose_name_plural = u"体验金活动"

    def __unicode__(self):
        return u'%s <%s>' % (self.id, self.name)


class ExperienceEventRecord(models.Model):
    event = models.ForeignKey(ExperienceEvent, verbose_name=u"体验金")
    user = models.ForeignKey(User, verbose_name=u"用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    apply = models.BooleanField(default=False, verbose_name=u"是否使用")
    apply_platform = models.CharField(max_length=20, null=False, default="", choices=PLATFORM, verbose_name=u"使用平台")
    apply_at = models.DateTimeField(verbose_name=u'使用时间', null=True)
    apply_amount = models.FloatField(null=True, default=0.0, verbose_name=u'使用金额')

    class Meta:
        verbose_name = u"体验金流水"
        verbose_name_plural = u"体验金流水"


class ExperienceAmortization(models.Model):
    product = models.ForeignKey(ExperienceProduct, related_name='experience_product_subs')
    user = models.ForeignKey(User)
    term = models.IntegerField(u'还款期数')
    term_date = models.DateTimeField(u'还款时间')

    principal = models.DecimalField(u'本金', max_digits=20, decimal_places=2)
    interest = models.DecimalField(u'利息', max_digits=20, decimal_places=2)

    settled = models.BooleanField(u'已结算', default=False)
    settlement_time = models.DateTimeField(u'结算时间', auto_now=False, null=True, blank=True)

    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    description = models.CharField(u'摘要', max_length=500, blank=True)

    class Meta:
        verbose_name_plural = u'体验标用户还款计划'

    def __unicode__(self):
        return u'用户%s 本金%s 利息%s' % (self.user, self.principal, self.interest)