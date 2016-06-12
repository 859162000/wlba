#!/usr/bin/env python
# encoding:utf-8

from decimal import Decimal
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from wanglibao_p2p.models import P2PProduct, ProductType
from django.core.exceptions import ValidationError


PLATFORM = (
    ("all", "全平台"),
    ("ios", "ios"),
    ("android", "android"),
    ("pc", "pc"),
    ("app", "移动端"),
    ("weixin", "微信"),
)


class RedPackEvent(models.Model):
    """
        根据红包规则创建不同的派发红包活动，创建有/无兑换码的活动
        兑换码红包不搞自动派发，如果是自动派发兑换码红包，需要更多的考虑(如前几名有红包，派发完就没有了)
    """
    EVENT_TYPE = (
        ("direct", u"直抵红包"),
        ("percent", u"投资百分比红包"),
        ("interest_coupon", u"加息券"),
    )
    PERIOD_TYPE = (
        ('month', u'月'),
        ('month_gte', u'月及以上'),
        ('month_lte', u'月及以下'),
        ('day', u'日'),
        ('day_gte', u'日及以上'),
        ('day_lte', u'日及以下'),
    )
    GIVE_MODE = (
        ("nil", u"零门槛(兑换码)"),
        ("activity", u"活动奖励"),
        ("register", u"注册"),
        ("validation", u"实名认证"),
        ("first_buy", u"首次投资"),
        ("first_pay", u"首次充值"),
        ('buy', u'投资'),
        ('pay', u'充值'),
        ('p2p_audit', u'满标审核'),
        ('repaid', u'还款'),
        ('first_bind_weixin', u'首次绑定微信'),
    )
    name = models.CharField(max_length=30, verbose_name=u'优惠券活动名字')
    rtype = models.CharField(max_length=20, verbose_name=u'优惠券类型', choices=EVENT_TYPE, default="直抵红包")
    amount = models.FloatField(null=False, default=0.0, verbose_name=u'优惠券金额(百分比也为0-100)')
    invest_amount = models.IntegerField(null=False, default=0, verbose_name=u"投资门槛")
    p2p_types = models.ForeignKey(ProductType, verbose_name=u"限定P2P分类", blank=True, null=True, on_delete=models.SET_NULL)
    period = models.IntegerField(default=0, max_length=200, verbose_name=u'限定产品期限', blank=True,
                                 help_text=u"填写整数数字")
    period_type = models.CharField(default='month', max_length=20, verbose_name=u'产品期限类型', choices=PERIOD_TYPE, blank=True)
    p2p_id = models.IntegerField(default=0, verbose_name=u"P2P标id,数字格式")
    highest_amount = models.IntegerField(null=False, default=0, verbose_name=u"最高抵扣金额(百分比使用0无限制)")
    value = models.IntegerField(null=False, default=0, verbose_name=u"优惠券个数(不生成兑换码无需修改)")
    describe = models.CharField(max_length=20, verbose_name=u"标注渠道批次等信息", default="")
    give_mode = models.CharField(max_length=20, verbose_name=u"发放方式", db_index=True, choices=GIVE_MODE, default=u"注册")
    give_platform = models.CharField(max_length=10, verbose_name=u"发放平台", default="全平台", choices=PLATFORM)
    apply_platform = models.CharField(max_length=10, verbose_name=u"使用平台", default="全平台", choices=PLATFORM)
    target_channel = models.CharField(max_length=1000, verbose_name=u"渠道(非邀请码)", blank=True, default="",
                                      help_text=u'不限渠道则留空即可（但是如果和活动配合使用，只要活动指定所有渠道，则不检测此处的内容）')
    give_start_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"发放/兑换开始时间")
    give_end_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"发放/兑换结束时间")
    available_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"生效时间")
    unavailable_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"失效时间")
    auto_extension = models.BooleanField(default=False, verbose_name=u"自动设定失效时间",
                                         help_text=u"选择此项后系统会将失效时间设置为具体发放日期加上失效延长天数")
    auto_extension_days = models.IntegerField(verbose_name=u"失效延长天数", default=0, null=False,
                                              help_text=u"如果填写了失效延长天数,系统会动态计算失效截止时间")
    invalid = models.BooleanField(default=False, verbose_name=u"是否作废")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta:
        verbose_name = u"优惠券活动"
        verbose_name_plural = u"优惠券活动"

    def __unicode__(self):
        return u'%s <%s>' % (self.id, self.name)


class RedPack(models.Model):
    """
        无兑换码一条记录
    """
    R_STATUS = (
        ("invalid", u"作废"),
        ("used", u"已兑换"),
        ("unused", u"未兑换"),
    )
    event = models.ForeignKey(RedPackEvent)
    token = models.CharField(max_length=20, verbose_name=u"兑换码", null=False, default="", db_index=True)
    status = models.CharField(max_length=20, verbose_name=u"兑换状态", choices=R_STATUS, default="unused")

    class Meta:
        verbose_name = u"优惠券列表"
        verbose_name_plural = u"优惠券列表"

    def __unicode__(self):
        return u'%s<%s-%s>' % (self.id, self.event.id, self.event.name)


class RedPackRecord(models.Model):
    redpack = models.ForeignKey(RedPack, verbose_name=u"优惠券")
    user = models.ForeignKey(User, verbose_name=u"用户")
    change_platform = models.CharField(max_length=20, null=False, default="", choices=PLATFORM, verbose_name=u"兑换平台")
    apply_platform = models.CharField(max_length=20, null=False, default="", choices=PLATFORM, verbose_name=u"使用平台")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    apply_at = models.DateTimeField(verbose_name=u'使用时间', null=True)
    apply_amount = models.FloatField(null=True, default=0.0, verbose_name=u'使用金额')
    is_month_product = models.BooleanField(default=False, verbose_name=u"是否是月利宝产品")
    order_id = models.IntegerField(verbose_name=u'关联订单', null=True, db_index=True)
    product_id = models.IntegerField(verbose_name=u'关联产品', null=True, db_index=True)

    class Meta:
        verbose_name = u"优惠券流水"
        verbose_name_plural = u"优惠券流水"


class InterestHike(models.Model):
    user = models.ForeignKey(User, verbose_name=u"用户")
    product = models.ForeignKey(P2PProduct, verbose_name=u"产品")
    rate = models.DecimalField(verbose_name=u'加息利率', max_digits=20, decimal_places=5, default=Decimal('0.00'))
    intro_total = models.IntegerField(verbose_name=u"此产品的邀请人数", default=0, blank=False, null=False)
    invalid = models.BooleanField(default=False, verbose_name=u"是否作废", null=False)
    paid = models.BooleanField(default=False, verbose_name=u"是否支付", null=False)
    amount = models.DecimalField(verbose_name=u'加息金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"创建时间")
    updated_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"更新时间")

    class Meta:
        verbose_name = u"加息券"
        verbose_name_plural = u"加息券"


# 佣金,加息等
class Income(models.Model):
    user = models.ForeignKey(User, verbose_name=u"用户", related_name="user")
    invite = models.ForeignKey(User, verbose_name=u"被邀请用户", related_name="invite")
    level = models.IntegerField(verbose_name=u"级别", default=0, blank=False, null=False)
    product = models.ForeignKey(P2PProduct, verbose_name=u"产品")
    amount = models.DecimalField(verbose_name=u'投资金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    earning = models.DecimalField(verbose_name=u'收益金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    order_id = models.IntegerField(verbose_name=u"订单号", default=0, blank=False, null=False)
    paid = models.BooleanField(verbose_name=u'已打款', default=False)
    created_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"创建时间")

    # Add by hb on 20-16-06-12
    class Meta:
        unique_together = (("user", "invite", "product"),)  # 联合唯一索引

# 新平台佣金单独处理
class PhpIncome(models.Model):
    user = models.ForeignKey(User, verbose_name=u"用户", related_name="php_user")
    invite = models.ForeignKey(User, verbose_name=u"被邀请用户", related_name="php_invite")
    level = models.IntegerField(verbose_name=u"级别", default=0, blank=False, null=False)
    product_id = models.IntegerField(verbose_name=u"月利宝ID", null=False)
    amount = models.DecimalField(verbose_name=u'投资金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    earning = models.DecimalField(verbose_name=u'收益金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    order_id = models.IntegerField(verbose_name=u"订单号", default=0, blank=False, null=False)
    paid = models.BooleanField(verbose_name=u'已打款', default=False)
    created_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"创建时间")

    # Add by hb on 20-16-06-12
    class Meta:
        unique_together = (("user", "invite", "product_id"),)  # 联合唯一索引

# 创建红包列表
def create_redpack(sender, instance, **kwargs):
    from wanglibao_redpack import tasks
    tasks.create_update_redpack.apply_async(kwargs={
        "event_id": instance.id
    })

post_save.connect(create_redpack, sender=RedPackEvent)
