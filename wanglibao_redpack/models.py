#!/usr/bin/env python
# encoding:utf-8

from django.db import models
from django.contrib.auth.models import User


class Rule(models.Model):
    """
        The red packet rule, create a different amount of it
    """
    name = models.CharField(max_length=20, verbose_name=u'红包名字')
    rtype = models.CharField(max_length=30, verbose_name=u'类型', choices=(
                ("direct", "直抵红包"),
                ("fullcut", "满减红包/最低投资额"),
                ("percent", "投资百分比红包"),))
    value = models.IntegerField(null=False, default=0, verbose_name=u'红包在不同类型大小')
    extra = models.CharField(max_length=30, verbose_name=u'扩展', null=False, default="")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta:
        verbose_name = u"红包规则"



give_type = (
    ("nil", "零门槛"),
    ("register", "注册"),
    ("validation", "实名认证"),
    ("first_buy", "首次投资"),
    ("first_pay", "首次充值"),
)


class RedPackEvent(models.Model):
    """
        根据红包规则创建不同的派发红包活动，创建有/无兑换码的活动
        自动派发的红包最后是普通的，创建一条，不再派发设为used即可
        兑换码红包不搞自动派发，如果是自动派发兑换码红包，需要更多的考虑(如前几名有红包，派发完就没有了)
    """
    name = models.CharField(max_length=20, verbose_name=u'活动名字')
    rule = models.ForeignKey(Rule)
    describe = models.CharField(max_length=20, verbose_name=u"标注渠道批次等信息", default="")
    give_mode = models.CharField(max_length=20, verbose_name=u"发放方式", default="", choices=give_type, db_index=True)
    give_start_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=u"发放开始时间")
    give_end_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=u"发放结束时间")
    available_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=u"生效时间")
    unavailable_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=u"失效时间")
    change_end_at = models.DateTimeField(null=True, verbose_name=u"兑换截止时间")
    extra = models.CharField(max_length=20, verbose_name=u"扩展字段", default="")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta:
        verbose_name = u"红包活动"

class RedPack(models.Model):
    """
        无兑换码一条记录
    """
    event = models.ForeignKey(RedPackEvent)
    token = models.CharField(max_length=20, verbose_name=u"兑换码", null=False, default="", db_index=True)
    status = models.CharField(max_length=20, verbose_name=u"状态", choices=(
                                ("invalid", "作废"),
                                ("used", "已用"),
                                ("unused", "未使用"),), default="unused")

class RedPackRecord(models.Model):
    PLATFORM = (
        ("ios", "ios"),
        ("android", "android"),
        ("pc", "pc"),
    )
    redpack = models.ForeignKey(RedPack)
    user = models.ForeignKey(User)
    #关联规则，减少查询
    rule = models.ForeignKey(Rule)
    change_platform = models.CharField(max_length=20, null=False, default="pc", choices=PLATFORM, verbose_name=u"兑换平台")
    apply_platform = models.CharField(max_length=20, null=False, default="pc", choices=PLATFORM, verbose_name=u"使用平台")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    apply_at = models.DateTimeField(verbose_name=u'使用时间', null=True)
    order_id = models.IntegerField(verbose_name=u'投资标的', null=True)
    available = models.BooleanField(default=False, verbose_name=u"是否可用")

    class Meta:
        verbose_name = u"红包流水"
