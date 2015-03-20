#!/usr/bin/env python
# encoding:utf-8

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


#class Rule(models.Model):
#    """
#        The red packet rule, create a different amount of it
#    """
#    name = models.CharField(max_length=20, verbose_name=u'红包名字')
#    rtype = models.CharField(max_length=30, verbose_name=u'类型', choices=(
#                ("direct", "直抵红包"),
#                ("fullcut", "满减红包/最低投资额"),
#                ("percent", "投资百分比红包"),))
#    amount = models.IntegerField(null=False, default=0, verbose_name=u'红包金额(百分比也为整数0-100)')
#    invest_amount = models.IntegerField(null=False, default=0, verbose_name=u"投资金额")
#    extra = models.CharField(max_length=30, verbose_name=u'扩展', default="", blank=True)
#    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
#
#    class Meta:
#        verbose_name = u"红包规则"
#        verbose_name_plural = u"红包规则"
#
#    def __unicode__(self):
#        if self.rtype == "direct":
#            return u'<%s> 直抵' % self.name
#        elif self.rtype == "fullcut":
#            return u'<%s> 满减' % self.name
#        else:
#            return u'<%s> 百分比' % self.name


PLATFORM = (
    ("all", "全平台"),
    ("ios", "ios"),
    ("android", "android"),
    ("pc", "pc"),
)

class RedPackEvent(models.Model):
    """
        根据红包规则创建不同的派发红包活动，创建有/无兑换码的活动
        兑换码红包不搞自动派发，如果是自动派发兑换码红包，需要更多的考虑(如前几名有红包，派发完就没有了)
    """
    name = models.CharField(max_length=30, verbose_name=u'红包活动名字')
    #rule = models.ForeignKey(Rule)
    rtype = models.CharField(max_length=20, verbose_name=u'红包类型', choices=(
                            ("direct", "直抵红包"),
                            #("fullcut", "满减红包/最低投资额"),
                            ("percent", "投资百分比红包"),), default="直抵红包")
    #amount = models.IntegerField(null=False, default=0, verbose_name=u'红包金额(百分比也为整数0-100)')
    amount = models.FloatField(null=False, default=0.0, verbose_name=u'红包金额(百分比也为0-100)')
    invest_amount = models.IntegerField(null=False, default=0, verbose_name=u"投资门槛")
    highest_amount = models.IntegerField(null=False, default=0, verbose_name=u"最高抵扣金额(百分比使用0无限制)")
    value = models.IntegerField(null=False, default=0, verbose_name=u"红包个数(不生成兑换码无需修改)")
    describe = models.CharField(max_length=20, verbose_name=u"标注渠道批次等信息", default="")
    give_mode = models.CharField(max_length=20, verbose_name=u"发放方式", db_index=True, choices=(
                                ("nil", u"零门槛(兑换码)"),
                                ("activity", u"活动奖励"),
                                ("register", u"注册"),
                                ("validation", u"实名认证"),
                                ("first_buy", u"首次投资"),
                                ("first_pay", u"首次充值"),
                                ('buy', u'投资'),
                                ('pay', u'充值')), default=u"注册")
    give_platform = models.CharField(max_length=10, verbose_name=u"发放平台", default="全平台", choices=PLATFORM)
    apply_platform = models.CharField(max_length=10, verbose_name=u"使用平台", default="全平台", choices=PLATFORM)
    target_channel = models.CharField(max_length=20, verbose_name=u"渠道(非邀请码)", blank=True, default="")
    give_start_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"发放/兑换开始时间")
    give_end_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"发放/兑换结束时间")
    available_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"生效时间")
    unavailable_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"失效时间")
    invalid = models.BooleanField(default=False, verbose_name=u"是否作废")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta:
        verbose_name = u"红包活动"
        verbose_name_plural = u"红包活动"

    def __unicode__(self):
        return u'%s <%s>' % (self.id, self.name)

class RedPack(models.Model):
    """
        无兑换码一条记录
    """
    event = models.ForeignKey(RedPackEvent)
    token = models.CharField(max_length=20, verbose_name=u"兑换码", null=False, default="", db_index=True)
    status = models.CharField(max_length=20, verbose_name=u"兑换状态", choices=(
                                ("invalid", "作废"),
                                ("used", "已兑换"),
                                ("unused", "未兑换"),), default="unused")

    class Meta:
        verbose_name = u"红包列表"
        verbose_name_plural = u"红包列表"

    def __unicode__(self):
        return u'%s<%s>' % (self.id, self.event.name)

class RedPackRecord(models.Model):
    redpack = models.ForeignKey(RedPack, verbose_name=u"红包")
    user = models.ForeignKey(User, verbose_name=u"用户")
    #rule = models.ForeignKey(Rule, verbose_name=u"规则")
    change_platform = models.CharField(max_length=20, null=False, default="", choices=PLATFORM, verbose_name=u"兑换平台")
    apply_platform = models.CharField(max_length=20, null=False, default="", choices=PLATFORM, verbose_name=u"使用平台")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    apply_at = models.DateTimeField(verbose_name=u'使用时间', null=True)
    order_id = models.IntegerField(verbose_name=u'关联订单', null=True)

    class Meta:
        verbose_name = u"红包流水"
        verbose_name_plural = u"红包流水"



#创建红包列表
def create_redpack(sender, instance, **kwargs):
    from wanglibao_redpack import tasks
    tasks.create_update_redpack.apply_async(kwargs={
        "event_id": instance.id
    })

post_save.connect(create_redpack, sender=RedPackEvent)
