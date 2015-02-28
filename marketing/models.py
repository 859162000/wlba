# coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from wanglibao_pay.util import get_a_uuid
from django.db import transaction
from decimal import *


class NewsAndReport(models.Model):
    name = models.CharField(u'名字', max_length=128)
    link = models.URLField(u'链接', null=True)
    score = models.IntegerField(u'排名权重', default=0)
    created_at = models.DateTimeField(u'添加时间', auto_now_add=True)
    image = models.ImageField(u'图片', null=True, upload_to='news', blank=True)

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


class IntroducedBy(models.Model):
    """ user: 被邀请人
        introduced_by: 邀请人
    """
    user = models.ForeignKey(User)
    introduced_by = models.ForeignKey(User, related_name='introduces')
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    bought_at = models.DateTimeField(u'第一次购买时间', null=True, blank=True)
    gift_send_at = models.DateTimeField(u'奖品发放时间', null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='creator')

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

    def get_earning(self, amount, months, type):
         return Decimal(amount*self.rule_amount*(Decimal(months)/Decimal(12))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

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
        (0, u'注册'),
        (1, u'购买'),
    )
    version = models.CharField(max_length=40)
    userdevice = models.CharField(max_length=120)
    network = models.CharField(max_length=30)
    channelid = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    action = models.IntegerField(max_length=2, choices=ACTION)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)


    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'客户端信息'


    def __unicode__(self):
        return u'<%s>' % self.userdevice


class IntroducedByReward(models.Model):
    """ 邀请奖励统计表"""
    STATUS = (
        (0, u'未审核'),
        (1, u'审核通过发放奖励'),
    )

    user = models.ForeignKey(User)
    introduced_by_person = models.ForeignKey(User, related_name='introduced_person')
    first_bought_at = models.DateTimeField(u'首笔购买时间', null=False)
    first_amount = models.DecimalField(u'首笔投资金额', max_digits=20, decimal_places=2, default=0)
    first_reward = models.DecimalField(u'首笔投资收益', max_digits=20, decimal_places=2, default=0)
    introduced_reward = models.DecimalField(u'首笔投资收益', max_digits=20, decimal_places=2, default=0)
    activity_start_at = models.DateTimeField(u'活动统计开始时间', null=False)
    activity_end_at = models.DateTimeField(u'活动统计截止时间', null=False)
    activity_amount_min = models.DecimalField(u'活动统计首笔投资最小金额', max_digits=20, decimal_places=2, default=0)
    percent_reward = models.DecimalField(u'活动奖励百分比奖励', max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    checked_status = models.IntegerField(u'审核状态', max_length=2, choices=STATUS)
    checked_at = models.DateTimeField(u'审核时间', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = u'邀请奖励统计表'
