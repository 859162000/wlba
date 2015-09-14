# coding=utf-8
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from wanglibao_activity.models import Activity


class WanglibaoActivityGiftGlobalCfg(models.Model):
    """
        活动发奖全局配置
    """
    activity = models.ForeignKey(Activity, default=None)
    chances = models.IntegerField(default=3, verbose_name=u'共有几次抽奖机会')
    when_register = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"什么时候注册的用户可以参与活动")

    class Meta:
        verbose_name = u'活动奖品全局配置'
        verbose_name_plural = u'活动奖品全局配置'


class WanglibaoActivityGift(models.Model):
    """ 活动发奖配置表 """
    TYPE = (
        (0, u'红包'),
        (1, u'加息券'),
        (2, u'优惠券'),
    )
    activity = models.ForeignKey(Activity, default=None)
    type = models.IntegerField(choices=TYPE, default=0, verbose_name=u'奖品类型')
    chances = models.IntegerField(default=3, verbose_name=u'配置用户有几次抽奖机会')
    name = models.CharField(max_length=128, default=u'红包', verbose_name=u'奖品名称', help_text=u'例如：红包、加息券、优惠券等')
    code = models.CharField(max_length=128, default="", verbose_name=u'奖品代码')
    rate = models.IntegerField(default=0, verbose_name=u'获奖概率', help_text=u"获奖概率请直接填写数字，例如：获奖概率为20%，填写 20")
    send_rate = models.IntegerField(default=0, verbose_name=u'发奖速度', help_text=u"发奖速度请直接填写数字,每天发多少个, 0表示每天不限量")
    count = models.IntegerField(default=0, verbose_name=u'奖品个数', help_text=u'如果为0，表示不限个数')
    channels = models.CharField(max_length=128, verbose_name=u'奖品发放渠道', help_text=u'各个渠道之间用空格分开; 如果为空，表示全渠道')
    valid = models.BooleanField(default=True, verbose_name=u'该奖项是否启动', help_text=u'奖项默认是启用的')
    class Meta:
        verbose_name = u'活动奖品配置'
        verbose_name_plural = u'活动奖品配置'


class WanglibaoUserGift(models.Model):
    """
        用户获奖记录
    """
    TYPE = (
        (0, u'红包'),
        (1, u'加息券'),
        (2, u'优惠券'),
    )
    SEND = (
        (0, u'YES'),
        (1, u'NO'),
        (2, u'INVALID')
    )
    user = models.ForeignKey(User)
    rules = models.ForeignKey(WanglibaoActivityGift, default=None)
    activity = models.ForeignKey(Activity)
    index = models.IntegerField(default=0, verbose_name=u'特定活动内的奖品编号')
    type = models.IntegerField(choices=TYPE, default=0, verbose_name=u'奖品类型')
    name = models.CharField(max_length=128, default=u'红包', verbose_name=u'奖品名称', help_text=u'例如：红包、加息券、优惠券等')
    valid = models.BooleanField(default=1, choices=SEND, verbose_name=u'奖品是否已发')
    class Meta:
        verbose_name = u'用户活动获奖记录'
        verbose_name_plural = u'用户活动获奖记录'

