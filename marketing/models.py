# coding=utf-8

from django.db import models
from django.core.exceptions import ValidationError


class Channels(models.Model):
    """
        渠道信息
    """
    _FROM = (
        ('full', u'全平台'),
        ('pc', u'电脑端'),
        ('mobile', u'移动端'),
        ('ios', u'苹果'),
        ('android', u'安卓'),
        ('ios+pc', u'苹果和电脑端'),
        ('android+pc', u'安卓和电脑端')
    )

    _CLASS = (
        ('----', '----'),
        ('CPC', u'CPC-按点击计费'),
        ('CPD', u'CPD-按天计费'),
        ('CPT', u'CPT-按时间计费'),
        ('CPA', u'CPA-按行为计费'),
        ('CPS', u'CPS-按销售计费')
    )

    _STATUS = (
        (0, u'0-正常'),
        (1, u'1-暂停拉新'),
        (2, u'2-暂停合作'),
        (3, u'3-渠道归并')
    )

    _CALLBACK = (
        ('register', u'注册'),
        ('validation', u'实名'),
        ('binding', u'绑卡'),
        ('first_investment', u'首投'),
        ('investment', u'投资'),
        ('first_pay', u'首充'),
        ('pay', u'充值')
    )

    code = models.CharField(u'渠道代码', max_length=12, db_index=True, unique=True)
    name = models.CharField(u'渠道名字', max_length=20, default="")
    description = models.CharField(u'渠道描述', max_length=50, default="", blank=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    image = models.ImageField(upload_to='channel', blank=True, default='',
                              verbose_name=u'渠道图片', help_text=u'主要用于渠道落地页的banner图片')
    coop_status = models.IntegerField(u'合作状态', max_length=2, default=0, choices=_STATUS)
    merge_code = models.CharField(u'并入渠道代码', blank=True, null=True, max_length=12)
    classification = models.CharField(u'渠道分类', max_length=20, default="----", choices=_CLASS)
    platform = models.CharField(u'渠道平台', max_length=20, default="full", choices=_FROM)
    start_at = models.DateTimeField(u'合作开始时间', blank=True, null=True, help_text=u'*可为空')
    end_at = models.DateTimeField(u'合作结束时间', blank=True, null=True, help_text=u'*可为空')
    is_abandoned = models.BooleanField(u'是否废弃', default=False)

    class Meta:
        verbose_name_plural = u"渠道"
        verbose_name = u"渠道"

    def clean(self):
        if len(self.code) == 6:
            raise ValidationError(u'为避免和邀请码重复，渠道代码长度不能等于6位')

        if self.coop_status == 3:
            if self.merge_code:
                ch = Channels.objects.filter(code=self.merge_code).first()
                if (not ch or ch.coop_status!=0 or ch.is_abandoned):
                    raise ValidationError(u'请输入正常状态的并入渠道代码')
                if (ch.code==self.code):
                    raise ValidationError(u'不能指定并入渠道为自己')
            else:
                raise ValidationError(u'设置状态为“渠道归并”时，请输入并入渠道代码')

    def __unicode__(self):
        return self.name
