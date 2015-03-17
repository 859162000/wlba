# coding=utf-8
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from wanglibao_redpack.models import RedPackEvent

PLATFORM = (
    ("all", u"全平台"),
    ("ios", u"ios"),
    ("android", u"android"),
    ("pc", u"pc"),
)
ACTIVITY_CATEGORY = (
    ('wanglibao', u'站内活动'),
    ('channel', u'渠道活动'),
    ('other', u'其他')
)
PRODUCT_CATEGORY = (
    ('all', u'所有产品'),
    ('p2p', u'P2P'),
    ('bill', u'票据'),
    ('ids', u'指定ID产品')
)
STATUS = (
    ('waiting', u'未开始'),
    ('active', u'进行中'),
    ('finished', u'已结束'),
    ('stopped', u'手动停止')
)
TRIGGER_NODE = (
    ('register', u'注册'),
    ('id_validate', u'实名认证'),
    ('recharge', u'充值'),
    ('invest', u'投资'),
    ('first_recharge', u'首次充值'),
    ('first_invest', u'首次投资'),
    ('', u'满标审核')
)
GIFT_TYPE = (
    ('reward', u'奖品'),
    ('redpack', u'红包'),
    ('income', u'收益'),
    ('phonefare', u'手机话费')
)


class Activity(models.Model):
    name = models.CharField(u'活动名称*', max_length=128)
    code = models.CharField(u'活动代码*', max_length=16, unique=True, help_text=u'字母或数字的组合')
    category = models.CharField(u'活动类型*', max_length=20, choices=ACTIVITY_CATEGORY, default=u'站内活动')
    platform = models.CharField(u'发布平台*', max_length=20, choices=PLATFORM, default=u'全平台')
    product_cats = models.CharField(u'指定产品范围', max_length=20, default=u'P2P产品', choices=PRODUCT_CATEGORY)
    product_ids = models.CharField(u'指定产品ID', max_length=20, blank=True, default=0, help_text=u"如果有多个产品，则产品ID之间用英文逗号分割")
    description = models.TextField(u'描述', null=True, blank=True)
    start_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"活动开始时间*")
    end_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"活动结束时间*")
    status = models.CharField(u'活动状态', max_length=20, choices=STATUS, default=u'未开始')
    stop_at = models.DateTimeField(null=True, verbose_name=u"手动停止时间", blank=True)
    created_at = models.DateTimeField(u'添加时间', auto_now_add=True)
    banner = models.ImageField(u'活动图片', null=True, upload_to='activity', blank=True)
    template = models.TextField(u'活动模板（pyjade编译过的模板）', null=True, blank=True)
    url = models.URLField(u'活动URL地址', null=True, blank=True)
    priority = models.IntegerField(u'优先级*', help_text=u'越大越优先', default=0, blank=False)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-priority']
        verbose_name_plural = u'活动管理'


class ActivityRule(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=u'活动名称')
    rule_name = models.CharField(u'规则名称', max_length=128)
    rule_description = models.TextField(u'规则描述', null=True, blank=True)
    gift_type = models.CharField(u'赠送类型', max_length=20, choices=GIFT_TYPE)
    trigger_node = models.CharField(u'触发节点', max_length=20, choices=TRIGGER_NODE)
    redpack = models.ForeignKey(RedPackEvent, verbose_name=u'红包类型', blank=True)
    reward = models.CharField(u'奖品类型名称', max_length=60, blank=True, help_text=u'类型名称一定要和奖品中的类型保持一致')
    income = models.FloatField(u'收益或收益率（送收益时填写）', default=0, blank=True, help_text=u'固定金额时填写大于1的数字，收益率时填写0-1之间的小数')
    min_amount = models.IntegerField(u'最小金额（投资或充值）', default=0)
    max_amount = models.IntegerField(u'最大金额（投资或充值）', default=0)
    msg_template = models.TextField(u'站内信模板（不填则不发）', blank=True, help_text=u'站内信模板不填写则触发该规则时不发站内信，如果有动态变量，用“%s”代替')
    sms_template = models.TextField(u'短信信模板（不填则不发）', blank=True, help_text=u'短信模板不填写则触发该规则时不发手机短信，如果有动态变量，用“%s”代替')
    created_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.rule_name

    class Meta:
        verbose_name_plural = u'活动规则'


class ActivityRecord(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=u'活动名称')
    rule = models.ForeignKey(ActivityRule, verbose_name=u'规则名称')
    platform = models.CharField(u'平台', max_length=20)
    trigger_node = models.CharField(u'触发节点', max_length=20, choices=TRIGGER_NODE)
    trigger_at = models.DateTimeField(u'触发时间', auto_created=False)
    description = models.TextField(u'摘要', blank=True)
    user = models.ForeignKey(User, verbose_name=u"触发用户")
    created_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'活动触发流水'

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = u'活动触发流水'


