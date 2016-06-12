# coding=utf-8

from django.db import models


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
        (u'注册', u'注册'),
        (u'实名', u'实名'),
        (u'绑卡', u'绑卡'),
        (u'绑卡', u'首投'),
        (u'首投', u'投资'),
        (u'首充', u'首充'),
        (u'绑卡', u'充值')
    )

    code = models.CharField(u'渠道代码', max_length=12, db_index=True, unique=True)
    name = models.CharField(u'渠道名字', max_length=20, default="")
    description = models.CharField(u'渠道描述', max_length=50, default="", blank=True)
    image = models.ImageField(upload_to='channel', blank=True, default='',
                              verbose_name=u'渠道图片', help_text=u'主要用于渠道落地页的banner图片')
    platform = models.CharField(u'渠道平台', max_length=20, default="full", choices=_FROM)

    coop_status = models.IntegerField(u'合作状态', max_length=2, default=0, choices=_STATUS)
    classification = models.CharField(u'渠道结算分类', max_length=20,  default=None, null=True, blank=True, choices=_CLASS)
    merge_code = models.CharField(u'并入渠道代码', blank=True, null=True, max_length=12)
    start_at = models.DateTimeField(u'合作开始时间', blank=True, null=True, help_text=u'*可为空')
    end_at = models.DateTimeField(u'合作结束时间', blank=True, null=True, help_text=u'*可为空')

    coop_callback = models.CharField(u'渠道回调', max_length=50, blank=True, null=True)
    disable_csrf = models.BooleanField(u'是否关闭CSRF校验', default=False, help_text=u'如关闭，需验签')
    sign_format = models.CharField(u'签名格式', max_length=50, blank=True,
                                   null=True, help_text=u'固定格式，如：{uid}{key}{phone}')

    coop_charge_name = models.CharField(u'渠道方负责人姓名', max_length=50, blank=True, null=True)
    coop_charge_phone = models.CharField(u'渠道方负责人联系电话', max_length=50, blank=True, null=True)

    is_abandoned = models.BooleanField(u'是否废弃', default=False)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = u"渠道"
        verbose_name = u"渠道"

    def __unicode__(self):
        return self.name


class ChannelParams(models.Model):
    PARAMS_SOURCES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('REQUEST', 'REQUEST'),
        ('BODY', 'BODY'),
        ('HEAD', 'HEAD'),
    )

    PARAMS_LEVEL = (
        (0, '0--一般参数'),
        (1, '1--父级参数'),
        (2, '2--子级参数'),
    )

    DECRYPT_METHOD = (
        ('json', 'json'),
        ('aes-128-ecb', 'aes-128-ecb'),
    )

    channel = models.ForeignKey(Channels, related_name='all_params')
    name = models.CharField(u'参数名', max_length=50, db_index=True)
    internal_name = models.CharField(u'内部参数名', max_length=50, null=True, blank=True)
    external_name = models.CharField(u'外部参数名', max_length=50)
    default_value = models.CharField(u'参数默认值', max_length=100, null=True, blank=True)
    get_from = models.CharField(u'参数获取', max_length=50, help_text=u'从request中获取')

    level = models.IntegerField(u'参数级别', max_length=2, default=0, choices=PARAMS_LEVEL)
    parent = models.CharField(u'父级参数名', max_length=50, null=True, blank=True)

    quote_url_decrypt = models.BooleanField(u'是否转义后解密', default=False)
    is_decrypt = models.BooleanField(u'是否需要解密', default=False)
    decrypt_method = models.CharField(u'解密方式', max_length=30, default=None, null=True, blank=True, choices=DECRYPT_METHOD)
    is_save_session = models.BooleanField(u'是否保存到session', default=False)
    is_join_sign = models.BooleanField(u'是否加入验签', default=False)

    description = models.CharField(u'参数描述', max_length=50, default="", blank=True)
    is_abandoned = models.BooleanField(u'是否废弃', default=False, db_index=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = u"渠道参数"
        verbose_name = u"渠道参数"
        unique_together = (("channel", "name"),)

    def __unicode__(self):
        return self.name
