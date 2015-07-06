# coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from wanglibao_pay.util import get_a_uuid
from django.db import transaction
from decimal import *
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError


class NewsAndReport(models.Model):
    name = models.CharField(u'名字', max_length=128)
    link = models.URLField(u'链接', null=True)
    score = models.IntegerField(u'排名权重', default=0)
    created_at = models.DateTimeField(u'添加时间', auto_now_add=True)
    image = models.ImageField(u'图片', null=True, upload_to='news', blank=True)
    keywords = models.CharField(u'关键字', max_length=200, null=True, blank=True, default='')
    description = models.TextField(u'描述', null=True, default='')
    content = RichTextField(default='', blank=True)
    hits = models.IntegerField(u'点击次数', blank=True, default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-score']
        verbose_name_plural = u'新闻报道'


class SiteData(models.Model):
    invest_threshold = models.IntegerField(u'起投额（元）', default=100)
    p2p_total_earning = models.DecimalField(u'投资人总收益', max_digits=20, decimal_places=2, default=0)
    p2p_total_trade = models.DecimalField(u'累计交易额', max_digits=20, decimal_places=2, default=0)
    earning_rate = models.CharField(u'年化收益率', max_length=16, default=u'10%-15%')
    highest_earning_rate = models.FloatField(u'最高年化收益率(%)', default=15)
    demand_deposit_interest_rate = models.FloatField(u'活期存款利率(%)', default=0.35)
    one_year_interest_rate = models.FloatField(u'一年期存款利率(%)', default=3)
    product_release_time = models.CharField(u'产品发布时间', max_length=128, default=u'17:30')
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'起投额 %d 总收益 %f 累计交易额 %f' % (self.invest_threshold, float(self.p2p_total_earning), float(self.p2p_total_trade))

    @property
    def demand_rate_times(self):
        return int(self.highest_earning_rate / self.demand_deposit_interest_rate)

    @property
    def one_year_times(self):
        return int(self.highest_earning_rate / self.one_year_interest_rate)

    class Meta:
        verbose_name_plural = u'网站数据'

class InviteCode(models.Model):
    code = models.CharField(u'邀请码', max_length=6, db_index=True, unique=True)
    is_used = models.BooleanField(u'是否使用', default=False)

    def __unicode__(self):
        return self.code

    class Meta:
        ordering = ['id']
        verbose_name_plural = u'原始邀请码'


class PromotionToken(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    token = models.CharField(u'推广代码', max_length=64, db_index=True, default=get_a_uuid)

    def __unicode__(self):
        return self.token

    class Meta:
        verbose_name_plural = u'用户邀请码'

class Channels(models.Model):
    """
        渠道信息
    """
    code = models.CharField(u'渠道代码', max_length=12, db_index=True, unique=True)
    name = models.CharField(u'渠道名字(xunlei)', max_length=20, default="")
    description = models.CharField(u'渠道描述', max_length=50, default="", blank=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = u"渠道"

    def clean(self):
        if len(self.code) == 6:
            raise ValidationError(u'为避免和邀请码重复，渠道代码长度不能等于6位')

    def __unicode__(self):
        return self.name

class IntroducedBy(models.Model):
    """ user: 被邀请人
        introduced_by: 邀请人
    """
    user = models.ForeignKey(User)
    introduced_by = models.ForeignKey(User, related_name='introduces', blank=True, null=True)
    channel = models.ForeignKey(Channels, blank=True, null=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    bought_at = models.DateTimeField(u'第一次购买时间', null=True, blank=True)
    gift_send_at = models.DateTimeField(u'奖品发放时间', null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='creator')
    product_id = models.IntegerField(u'产品ID', default=0, null=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = u'邀请关系'


def generate_user_promo_token_and_invitecode(sender, instance, **kwargs):
    if kwargs["created"]:
        with transaction.atomic():
            invite_code = InviteCode.objects.select_for_update().filter(is_used=False).first()
            invite_code.is_used = True
            invite_code.save()

        p = PromotionToken()
        p.token = invite_code.code
        p.user = instance
        p.save()


def generate_user_promo_token(sender, instance, **kwargs):
    if kwargs["created"]:
        p = PromotionToken()
        p.user = instance
        p.save()


# post_save.connect(generate_user_promo_token, sender=User, dispatch_uid="generate_promotion_token")
post_save.connect(generate_user_promo_token_and_invitecode, sender=User, dispatch_uid="generate_promotion_token")


class TimelySiteData(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    p2p_margin = models.DecimalField(u'P2P余额', max_digits=20, decimal_places=2, default=0)
    freeze_amount = models.DecimalField(u'投资中冻结金额', max_digits=20, decimal_places=2, default=0)
    total_amount = models.DecimalField(u'总额', max_digits=20, decimal_places=2, default=0)
    user_count = models.IntegerField(u'用户总数', default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = u'交易数据'

class ActivityRule(models.Model):
    """ author: hetao
        datetime: 2014.10.27
        description: 市场活动规则
    """
    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'返现活动规则'

    name = models.CharField(u'规则名称', max_length=128)
    description = models.TextField(u'规则描述')

    rule_type = models.CharField(u'规则类型', max_length=50, null=False)
    rule_amount = models.DecimalField(u'数额', max_digits=20, decimal_places=4, default=0)
    create_time = models.DateTimeField(u'活动创建时间', auto_now_add=True)

    @property
    def percent_text(self):
        return Decimal(self.rule_amount*100).quantize(Decimal('0.1'))

    def get_earning(self, amount, period, pay_method):
        CALCULATE_METHOD_MONTH = 'monthly'
        CALCULATE_METHOD_DAY = 'daily'

        pay_method_mapping = {
                u'等额本息': CALCULATE_METHOD_MONTH,
                u'按月付息': CALCULATE_METHOD_MONTH,
                u'到期还本付息': CALCULATE_METHOD_MONTH ,
                u'日计息一次性还本付息': CALCULATE_METHOD_DAY,
                u'日计息月付息到期还本': CALCULATE_METHOD_DAY 
                }

        base_period = Decimal(12)
        if pay_method_mapping.get(pay_method) == CALCULATE_METHOD_DAY:
            base_period = Decimal(360)

        return Decimal(amount*self.rule_amount*(Decimal(period)/base_period))\
                .quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    def __unicode__(self):
        return u'<%s>' % self.name


class Activity(models.Model):
    """ author: hetao
        datetime: 2014.10.27
        description: 市场活动
    """
    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'返现活动'

    name = models.CharField(u'活动名称', max_length=128)
    description = models.TextField(u'活动描述')

    rule = models.ForeignKey(ActivityRule, help_text=u'活动规则', null=True, on_delete=models.SET_NULL, blank=False)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    start_time = models.DateTimeField(u'开始时间')
    end_time = models.DateTimeField(u'结束时间')

    def __unicode__(self):
        return u'<%s %s>' % (self.name, self.description)


class Reward(models.Model):
    """ 奖品存储
    """

    type = models.CharField(u'奖品类型', max_length=40)
    description = models.TextField(u'奖品描述', null=True)
    content = models.CharField(u'奖品内容', max_length=128)
    is_used = models.BooleanField(u'是否使用', default=False)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    end_time = models.DateTimeField(u'结束时间', null=True, blank=True)

    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'奖品'

    def __unicode__(self):
        return u'<%s>' % self.type


class RewardRecord(models.Model):
    """ 奖品发放流水
    """
    user = models.ForeignKey(User)
    reward = models.ForeignKey(Reward)
    description = models.TextField(u'发放奖品流水说明', null=True)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'奖品发放流水'

    def __unicode__(self):
        return u'<%s>' % self.user


class ClientData(models.Model):
    """ 统计客户端信息 """
    ACTION = (
        ('R', u'注册'),
        ('L', u'登录'),
        ('V', u'实名认证'),
        ('D', u'充值'),
        ('B', u'购买'),
        ('W', u'提现'),
    )
    version = models.CharField(max_length=40, blank=False, null=False, default="")
    userdevice = models.CharField(max_length=40, blank=False, null=False, default="")
    os = models.CharField(max_length=20, blank=False, null=False, default="")
    os_version = models.CharField(max_length=30, blank=False, null=False, default="")
    network = models.CharField(max_length=30, blank=False, null=False, default="")
    channel = models.CharField(max_length=50, blank=False, null=False, default="")
    user_id = models.IntegerField(u"用户ID", blank=False, null=False, default=0)
    amount = models.DecimalField(u'金额', max_digits=20, decimal_places=2, default=0)
    action = models.CharField(max_length=10, blank=False, null=False, choices=ACTION)
    create_time = models.DateTimeField(u'创建时间', blank=False, null=False, default=timezone.now)


    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'客户端信息'

    def __unicode__(self):
        return u'<%s>' % self.userdevice


class IntroducedByReward(models.Model):
    from wanglibao_p2p.models import P2PProduct

    """ 邀请奖励统计表"""
    STATUS = (
        (0, u'未审核'),
        (1, u'审核通过发放奖励'),
    )

    user = models.ForeignKey(User)
    introduced_by_person = models.ForeignKey(User, related_name='introduced_person', blank=True, null=True)
    product = models.ForeignKey(P2PProduct, help_text=u'投资标的', blank=True, null=True, default=None)
    first_bought_at = models.DateTimeField(u'首笔购买时间', null=False)
    first_amount = models.DecimalField(u'首笔投资金额', max_digits=20, decimal_places=2, default=0)
    first_reward = models.DecimalField(u'首笔投资收益', max_digits=20, decimal_places=2, default=0)
    introduced_reward = models.DecimalField(u'邀请人奖励', max_digits=20, decimal_places=2, default=0)
    activity_start_at = models.DateTimeField(u'活动统计开始时间', null=False)
    activity_end_at = models.DateTimeField(u'活动统计截止时间', null=False)
    activity_amount_min = models.DecimalField(u'活动统计首笔投资最小金额', max_digits=20, decimal_places=2, default=0)
    percent_reward = models.DecimalField(u'活动奖励百分比奖励', max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    checked_status = models.IntegerField(u'审核状态', max_length=2, choices=STATUS)
    checked_at = models.DateTimeField(u'审核时间', null=True, blank=True)
    user_send_status = models.BooleanField(u'被邀请人发放状态', default=False)
    user_send_amount = models.DecimalField(u'被邀请人发放金额', max_digits=20, decimal_places=2, default=0)
    introduced_send_status = models.BooleanField(u'邀请人发放状态', default=False)
    introduced_send_amount = models.DecimalField(u'邀请人发放金额', max_digits=20, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = u'邀请奖励统计表'


class PlayList(models.Model):
    """ 活动打榜奖励 """
    STATUS = (
        (0, u'未审核'),
        (1, u'审核通过'),
        (2, u'发放红包成功'),
    )

    play_at = models.DateTimeField(u'活动统计开始时间', null=False)
    user = models.ForeignKey(User)
    amount = models.DecimalField(u'投资金额', max_digits=20, decimal_places=2, default=0)
    ranking = models.IntegerField(u'排名', max_length=10, null=True, blank=True, default=0)
    # redpackevent = models.IntegerField(u'活动', max_length=10, null=True, blank=True, default=0)
    redpackevent = models.TextField(u'活动红包名称', null=False)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    checked_status = models.IntegerField(u'审核状态', max_length=2, choices=STATUS, default=0)
    amount_min = models.DecimalField(u'奖励开始金额', max_digits=20, decimal_places=2, default=0)
    amount_max = models.DecimalField(u'奖励截止金额', max_digits=20, decimal_places=2, default=0)
    start = models.IntegerField(u'奖励开始名次', max_length=2, null=True, blank=True)
    end = models.IntegerField(u'奖励截止名次', max_length=2, null=True, blank=True)
    reward = models.DecimalField(u'红包奖励金额', max_digits=20, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = u'打榜统计表'


class ActivityJoinLog(models.Model):
    """参加活动的用户记录"""
    user = models.ForeignKey(User)
    action_name = models.CharField(u'活动名称', max_length=200)
    action_type = models.CharField(u'参加类型', max_length=100)
    action_message = models.TextField(u'摘要', blank=True)
    join_times = models.IntegerField(u'参加次数', max_length=6, default=0)
    gift_name = models.CharField(u'奖品名称', max_length=200, blank=True)
    amount = models.DecimalField(u'奖品金额', max_digits=10, decimal_places=2, default=0)
    channel = models.CharField(u'渠道', max_length=100, blank=True)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = u'用户参加活动记录'

    def __unicode__(self):
        return self.action_name
