# coding=utf-8
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from wanglibao_redpack.models import RedPackEvent
from ckeditor.fields import RichTextField

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
    ('validation', u'实名认证'),
    ('pay', u'充值'),
    ('buy', u'投资'),
    ('first_pay', u'首次充值'),
    ('first_buy', u'首次投资'),
    ('p2p_audit', u'满标审核')
)
GIFT_TYPE = (
    ('reward', u'奖品'),
    ('redpack', u'红包'),
    ('income', u'收益'),
    ('phonefare', u'手机话费')
)
SEND_TYPE = (
    ('sys_auto', u'系统实时发放'),
    ('manual_operation', u'人工手动发放')
)
MSG_TYPE = (
    ('message', u'站内信'),
    ('sms', u'手机短信'),
    ('only_record', u'只记录')
)


class Activity(models.Model):
    name = models.CharField(u'活动名称*', max_length=128)
    code = models.CharField(u'活动代码*', max_length=16, unique=True, help_text=u'字母或数字的组合')
    category = models.CharField(u'活动类型*', max_length=20, choices=ACTIVITY_CATEGORY, default=u'站内活动')
    platform = models.CharField(u'发布平台*', max_length=20, choices=PLATFORM, default=u'全平台')
    product_cats = models.CharField(u'指定产品范围', max_length=20, default=u'P2P产品', choices=PRODUCT_CATEGORY)
    product_ids = models.CharField(u'指定产品ID', max_length=20, blank=True, default='', help_text=u"如果有多个产品，则产品ID之间用英文逗号分割")
    description = models.TextField(u'描述', null=True, blank=True)
    channel = models.CharField(u'渠道代码', max_length=20, blank=True, help_text=u'如果选择“渠道活动”，则填入对应渠道的渠道代码')
    start_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"活动开始时间*")
    end_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"活动结束时间*")
    is_stopped = models.BooleanField(u'是否手工停止', default=False)
    stopped_at = models.DateTimeField(null=True, verbose_name=u"手动停止时间", blank=True)
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

    def clean(self):
        if self.category == 'channel' and not self.channel:
            raise ValidationError(u'当活动类型为渠道时，要填入channel代码')
        if self.category == 'wanglibao' and not self.channel:
            self.channel = 'wanglibao'
        if self.start_at >= self.end_at:
            raise ValidationError(u'开始时间不能大于或等于结束时间')
        if self.product_cats == 'ids' and (self.product_ids == '0' or not self.product_ids):
            raise ValidationError(u'选择指定产品时，需要填写产品的ID，多个ID之间用英文逗号间隔')
        if self.is_stopped:
            self.stopped_at = timezone.now()


class ActivityRule(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=u'活动名称')
    rule_name = models.CharField(u'规则名称', max_length=128)
    rule_description = models.TextField(u'规则描述', null=True, blank=True)
    gift_type = models.CharField(u'赠送类型', max_length=20, choices=GIFT_TYPE)
    trigger_node = models.CharField(u'触发节点', max_length=20, choices=TRIGGER_NODE)
    is_introduced = models.BooleanField(u'邀请好友时才启用', default=False,
                                        help_text=u'勾选此项则，则会先判断用户是否被别人邀请，是就触发该规则，不是则不做处理')
    both_share = models.BooleanField(u'参与邀请共享赠送礼品', default=False,
                                     help_text=u'勾选此项则，则用户在满足规则的条件内邀请别人，双方共享选定“赠送类型”中的礼品')
    redpack = models.CharField(u'红包活动ID', max_length=60, blank=True,
                               help_text=u'红包活动ID一定要和红包活动中的ID保持一致，否则会导致无法发放红包')
    reward = models.CharField(u'奖品类型名称', max_length=60, blank=True,
                              help_text=u'奖品类型名称一定要和奖品中的类型保持一致，否则会导致无法发放奖品')
    income = models.FloatField(u'金额或比率', default=0, blank=True,
                               help_text=u'选择收益或话费时填写，固定金额时填写大于1的数字，收益率时填写0-1之间的小数')
    min_amount = models.IntegerField(u'最小金额', default=0,
                                     help_text=u'投资或充值，大于该金额（>），当只有最小金额时为大于等于该金额（>=）')
    max_amount = models.IntegerField(u'最大金额', default=0,
                                     help_text=u'投资或充值，小于等于该金额（<=）')
    msg_template = models.TextField(u'站内信模板（不填则不发）', blank=True,
                                    help_text=u'站内信模板不填写则触发该规则时不发站内信，变量写在2个大括号之间，<br/>\
                                              内置：注册人手机：“{{ mobile }}，奖品激活码：{{ reward }}，截止日期{{end_date}}<br/>\
                                              邀请人：{{ inviter }}，被邀请人：{{ invited }}，金额或百分比{{ amount }}<br/>\
                                              活动名称：{{ name }}，红包最高抵扣金额：{{ highest_amount }}”')
    sms_template = models.TextField(u'短信模板（不填则不发）', blank=True,
                                    help_text=u'短信模板不填写则触发该规则时不发手机短信，变量写在2个大括号之间，变量：同上')
    msg_template_introduce = models.TextField(u'邀请人站内信模板', blank=True,
                                              help_text=u'邀请人站内信模板不填写则不发送，变量写在2个大括号之间，变量：同上')
    sms_template_introduce = models.TextField(u'邀请人短信模板', blank=True,
                                              help_text=u'邀请人短信模板不填写则不发送，变量写在2个大括号之间，变量：同上')
    send_type = models.CharField(u'赠送发放方式', max_length=20, choices=SEND_TYPE,
                                 default=u'系统实时发放')
    created_at = models.DateTimeField(auto_now=True)
    is_used = models.BooleanField(u'是否启用', default=False)

    def __unicode__(self):
        return self.rule_name

    class Meta:
        verbose_name_plural = u'活动规则'

    def clean(self):
        if self.gift_type == 'reward' and not self.reward:
            raise ValidationError(u'赠送类型为“奖品”时，必须填写“奖品类型名称”')
        if self.gift_type == 'redpack' and not self.redpack:
            raise ValidationError(u'赠送类型为“红包”时，必须填写“红包类型ID”')
        if self.gift_type == 'income' or self.gift_type == 'phonefare':
            if self.income <= 0:
                raise ValidationError(u'选择送收益或手机话费时要填写“金额或比率”')
        if self.min_amount > 0 and self.max_amount > 0:
            if self.min_amount >= self.max_amount:
                raise ValidationError(u'最小金额和最大金额都大于0时，最大金额必须大于最小金额')


class ActivityRecord(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=u'活动名称')
    rule = models.ForeignKey(ActivityRule, verbose_name=u'规则名称')
    platform = models.CharField(u'平台', max_length=20)
    trigger_node = models.CharField(u'触发节点', max_length=20, choices=TRIGGER_NODE)
    trigger_at = models.DateTimeField(u'触发时间', auto_created=False)
    description = models.TextField(u'摘要', blank=True)
    msg_type = models.CharField(u'信息类型', max_length=20, choices=MSG_TYPE, default=u"只记录")
    user = models.ForeignKey(User, verbose_name=u"触发用户")
    income = models.FloatField(u'费用或收益', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'活动触发流水'

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = u'活动触发流水'


class ActivityImages(models.Model):
    """ the list of templates images """

    IMG_TYPE = (
        ('reward', u'赠送礼包'),
        ('register', u'注册流程'),
    )

    img_type = models.CharField(max_length=20, choices=IMG_TYPE, verbose_name=u'图片类别')
    name = models.CharField(max_length=128, verbose_name=u'图片名称', help_text=u'当图片类别是元素时,模板中会显示')
    img = models.ImageField(upload_to='activity', blank=True, verbose_name=u'图片')
    desc_one = models.CharField(max_length=1024, blank=True, verbose_name=u'图片描述1', help_text=u'展示在图片旁边的描述信息')
    desc_two = models.CharField(max_length=1024, blank=True, verbose_name=u'图片描述2', help_text=u'展示在图片旁边的描述信息')
    priority = models.IntegerField(verbose_name=u'优先级', help_text=u'越大越优先')
    last_updated = models.DateTimeField(auto_now=True, verbose_name=u'更新时间', help_text=u'上次更新时间')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'模板图片'


class ActivityTemplates(models.Model):
    """ the templates of activity """

    OPEN_CHOICE = (
        (0, u'关闭此模块'),
        (1, u'加载默认模块'),
        (2, u'加载自定义设置'),
    )

    name = models.CharField(u'活动时间描述', max_length=128, blank=True, help_text=u'例如<活动时间：2015-03-18至2015-03-28>')
    # logo
    logo = models.ImageField(u'网利宝logo图片', null=True, upload_to='activity', blank=True)
    logo_other = models.ImageField(u'第三方logo图片', null=True, upload_to='activity', blank=True)
    location = models.BooleanField(u'是否改变logo顺序', default=False, help_text=u'勾选此项则，则网利宝logo在后，第三方logo在前')
    # banner
    banner = models.ImageField(u'banner图片', null=True, upload_to='activity', blank=True)
    # 活动时间及描述
    is_activity_desc = models.IntegerField(u'加载活动时间及描述模块方案', max_length=20, choices=OPEN_CHOICE, default=0)
    desc = models.CharField(u'活动描述', max_length=1024, blank=True, help_text=u'例如<一句话描述，活动期间怎么怎么滴>')
    desc_time = models.CharField(u'活动时间', max_length=1024, blank=True, help_text=u'例如<活动时间：2015-03-18至2015-03-28>')
    # 活动奖品图片及描述
    is_reward = models.IntegerField(u'加载活动奖品模块方案', max_length=20, choices=OPEN_CHOICE, default=0)
    reward_img = models.CharField(u'活动奖品图片ID:', max_length=60, blank=True, null=True, help_text=u'如果有多个图片，则图片ID之间用英文逗号分割')
    reward_desc = RichTextField(u'奖品描述', blank=True, null=True)
    # 好友邀请及描述
    is_introduce = models.IntegerField(u'加载邀请好友模块方案', max_length=20, choices=OPEN_CHOICE, default=0, help_text=u'当选择加载自定义设置时，自定义内容才会被加载到模板中')
    introduce_desc = RichTextField(u'邀请好友描述', blank=True, null=True)
    introduce_img = RichTextField(u'邀请好友指定图片ID:', blank=True, null=True, help_text=u'如果有多个图片，则图片ID之间用英文逗号分割')
    # 新手投资流程
    is_teacher = models.IntegerField(u'加载活动奖品模块方案', max_length=20, choices=OPEN_CHOICE, default=0)
    teacher_desc = RichTextField(u'新手投资模块描述', blank=True, null=True)
    # 规则描述
    is_rule_use = models.IntegerField(u'加载活动使用规则模块方案', max_length=20, choices=OPEN_CHOICE, default=0)
    rule_use = RichTextField(verbose_name=u'使用规则', blank=True, null=True)
    is_rule_activity = models.IntegerField(u'加载活动规则模块方案', max_length=20, choices=OPEN_CHOICE, default=0)
    rule_activity = RichTextField(verbose_name=u'活动规则', blank=True, null=True)
    is_rule_reward = models.IntegerField(u'加载奖品发放规则模块方案', max_length=20, choices=OPEN_CHOICE, default=0)
    rule_reward = RichTextField(verbose_name=u'奖品发放', blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'活动模板'

    def clean(self):
        if self.is_activity_desc == 2:
            if not self.desc:
                raise ValidationError(u'选择自定义设置方案时，必须填写“活动描述”')
            if not self.desc_time:
                raise ValidationError(u'选择自定义设置方案时，必须填写“活动时间”')
        if self.is_reward == 2:
            if not self.reward_img:
                raise ValidationError(u'选择自定义设置方案时，必须填写“活动奖品图片ID”')
            if not self.reward_desc:
                raise ValidationError(u'选择自定义设置方案时，必须填写“奖品描述”')
        if self.is_introduce == 2:
            if not self.introduce_desc:
                raise ValidationError(u'选择自定义设置方案时，必须填写“邀请好友描述”')
            if not self.introduce_img:
                raise ValidationError(u'选择自定义设置方案时，必须填写“邀请好友指定图片ID”')
        if self.is_teacher == 2 and not self.teacher_desc:
                raise ValidationError(u'选择自定义设置方案时，必须填写“新手投资模块描述”')

        if self.is_rule_use == 2 and not self.rule_use:
            raise ValidationError(u'选择自定义设置方案时，必须填写“使用规则”')

        if self.is_rule_activity == 2 and not self.rule_activity:
            raise ValidationError(u'选择自定义设置方案时，必须填写“活动规则”')

        if self.is_rule_reward == 2 and not self.rule_reward:
            raise ValidationError(u'选择自定义设置方案时，必须填写“奖品发放”')
