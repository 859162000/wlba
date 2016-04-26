# coding=utf-8
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from wanglibao_redpack.models import RedPackEvent
from wanglibao_p2p.models import ProductType
from datetime import timedelta

PLATFORM = (
    ("all", u"全平台"),
    ("ios", u"ios"),
    ("android", u"android"),
    ("pc", u"pc"),
    ('weixin', u"weixin"),
)
ACTIVITY_CATEGORY = (
    ('wanglibao', u'站内活动'),
    ('channel', u'渠道活动'),
    ('other', u'其他')
)
PRODUCT_CATEGORY = (
    ('all', u'所有产品'),
    ('p2p', u'P2P'),
    #('bill', u'票据'),
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
    ('p2p_audit', u'满标审核'),
    ('repaid', u'还款'),
    ('activity', u'活动奖励'),
    ('first_bind_weixin', u'首次绑定微信')
)
GIFT_TYPE = (
    ('reward', u'奖品'),
    ('redpack', u'优惠券'),
    ('experience_gold', u'体验金'),
    # ('phonefare', u'手机话费')
)
SEND_TYPE = (
    ('sys_auto', u'系统实时发放'),
    # ('manual_operation', u'人工手动发放')
)
SEND_TYPE_ABBR = (
    ('sys_auto', u'系统'),
    ('manual_operation', u'人工')
)
MSG_TYPE = (
    ('message', u'站内信'),
    ('sms', u'手机短信'),
    ('only_record', u'只记录')
)
SHARE_TYPE = (
    ('both', u'邀请人和被邀请人双方共享'),
    ('inviter', u'邀请人独自获得'),
)
WX_TEMPLATE_CHOICE = (
    ('first_bind', u'首次绑定微信'),
)


class Activity(models.Model):
    name = models.CharField(u'活动名称*', max_length=128)
    code = models.CharField(u'活动代码*', max_length=64, unique=True, help_text=u'字母或数字的组合')
    category = models.CharField(u'活动类型*', max_length=20, choices=ACTIVITY_CATEGORY, default=u'站内活动')
    platform = models.CharField(u'发布平台*', max_length=20, choices=PLATFORM, default=u'全平台')
    product_cats = models.CharField(u'指定产品范围', max_length=20, default=u'P2P产品', choices=PRODUCT_CATEGORY)
    product_ids = models.CharField(u'指定产品ID', max_length=200, blank=True, default='',
                                   help_text=u"如果有多个产品，则产品ID之间用英文逗号分割")
    description = models.TextField(u'描述', null=True, blank=True)
    is_lottery = models.BooleanField(u'是否为抽奖活动', default=False, editable=False)
    chances = models.IntegerField(u'抽奖次数', default=0, blank=True, null=True, editable=False)
    rewards = models.IntegerField(u'获奖次数', default=0, blank=True, null=True, editable=False)
    channel = models.CharField(u'渠道名称', max_length=1000, blank=True,
                               help_text=u'如果是对应渠道的活动，则填入对应渠道的渠道名称代码，默认为wanglibao-other，多个渠道用英文逗号间隔')
    is_all_channel = models.BooleanField(u'所有渠道', default=False, help_text=u'如果勾选“所有渠道”，则系统不再限定渠道')
    start_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"活动开始时间*")
    end_at = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"活动结束时间*")
    is_stopped = models.BooleanField(u'是否停止', default=False)
    stopped_at = models.DateTimeField(null=True, verbose_name=u"停止时间", blank=True)
    created_at = models.DateTimeField(u'添加时间', default=timezone.now, auto_now_add=True)
    banner = models.ImageField(u'活动图片', null=True, upload_to='activity', blank=True)
    template = models.TextField(u'活动模板（pyjade编译过的模板）', null=True, blank=True)
    url = models.URLField(u'活动URL地址', null=True, blank=True)
    priority = models.IntegerField(u'优先级*', help_text=u'越大越优先', default=0, blank=False)

    def __unicode__(self):
        return '(%s)%s' % (self.id, self.name)

    class Meta:
        ordering = ['-priority']
        verbose_name_plural = u'活动管理'

    def clean(self):
        if self.category == 'channel' and not self.channel:
            raise ValidationError(u'当活动类型为渠道时，要填入channel代码')
        if self.category == 'wanglibao' and not self.channel:
            self.channel = 'wanglibao-other'
        if self.start_at >= self.end_at:
            raise ValidationError(u'开始时间不能大于或等于结束时间')
        if self.product_cats == 'ids' and (self.product_ids == '0' or not self.product_ids):
            raise ValidationError(u'选择指定产品时，需要填写产品的ID，多个ID之间用英文逗号间隔')
        if self.is_stopped:
            self.stopped_at = timezone.now()
        if self.chances < self.rewards:
            raise ValidationError(u'获奖次数不能大于抽奖次数')

    def activity_status(self):
        now = timezone.now()
        if self.is_stopped:
            return u'手工停止'
        else:
            if self.start_at > now:
                return u'未开始'
            elif self.end_at < now:
                return u'已结束'
            else:
                return u'进行中'

    activity_status.short_description = u'活动状态'
    activity_status.allow_tags = True


class ActivityRule(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=u'活动名称')
    rule_name = models.CharField(u'规则名称', max_length=128)
    rule_description = models.TextField(u'规则描述', null=True, blank=True)
    gift_type = models.CharField(u'赠送类型', max_length=20, choices=GIFT_TYPE)
    trigger_node = models.CharField(u'触发节点', max_length=20, choices=TRIGGER_NODE)
    p2p_types = models.ForeignKey(ProductType, verbose_name=u"限定P2P分类", blank=True, null=True, on_delete=models.SET_NULL)
    period = models.IntegerField(default=0, verbose_name=u'限定产品期限', blank=True, help_text=u"填写整数数字")
    period_type = models.CharField(default='month', max_length=20, verbose_name=u'产品期限类型', choices=(
        ('month', u'月'),
        ('month_gte', u'月及以上'),
        ('day', u'日'),
        ('day_gte', u'日及以上'),
    ), blank=True, help_text=u"产品限定只对[投资/首次投资]有效")
    is_in_date = models.BooleanField(u'判断首次充值（或首次投资）的时间是否在活动时间内', default=False,
                                     help_text=u'勾选此项，则会以活动的起止时间来判断首次投资或充值的动作，否则不做时间判断')
    is_introduced = models.BooleanField(u'邀请好友时才启用', default=False,
                                        help_text=u'勾选此项，则会先判断用户是否被别人邀请，是就触发该规则，不是则不做处理')
    share_type = models.CharField(u'选择参与赠送的人员', max_length=20, choices=SHARE_TYPE, blank=True, default='')
    is_invite_in_date = models.BooleanField(u'判断是否在活动区间内邀请好友', default=False,
                                            help_text=u'勾选此项则，则会先判断邀请关系的成立时间是否在活动期间，是就触发该规则，不是则不做处理')
    redpack = models.CharField(u'对应活动ID', max_length=200, blank=True,
                               help_text=u'优惠券活动ID/体验金活动ID一定要和对应活动中的ID保持一致，否则会导致无法发放<br/>\
                               如需要多个ID则用英文逗号隔开,如:1,2,3')
    probability = models.FloatField(u'获奖概率', default=0, blank=True, null=True, editable=False)
    reward = models.CharField(u'奖品类型名称', max_length=200, blank=True,
                              help_text=u'奖品类型名称一定要和奖品中的类型保持一致，否则会导致无法发放奖品')
    income = models.FloatField(u'金额或比率', default=0, blank=True,
                               help_text=u'选择收益或话费时填写，固定金额时填写大于1的数字，收益率时填写0-1之间的小数')
    min_amount = models.IntegerField(u'最小金额', default=0,
                                     help_text=u'投资/充值/持仓/还款本金，大于该金额（>），当只有最小金额时为大于等于该金额（>=）')
    max_amount = models.IntegerField(u'最大金额', default=0,
                                     help_text=u'投资/充值/持仓/还款本金，小于等于该金额（<=）')
    is_total_invest = models.BooleanField(u'启用满标累计投资', default=False,
                                          help_text=u'勾选该选项，则最大、最小金额视为累计投资金额，系统会在满标时检测用户在当前标的中的累计投资金额')
    total_invest_order = models.IntegerField(u'满标累计投资排名', blank=True, default=0,
                                             help_text=u'只能填写大于1的数字<br/>\
                                                       默认为0时只判断投资总额是否符合最大/最小金额区间<br/>\
                                                       如果设置最大/最小金额，则会判断用户投资总额是否符合最大/最小金额区间')
    ranking = models.IntegerField(u'单标投资顺序', blank=True, default=0,
                                  help_text=u'设置单个标的投资顺序，只能填写-1或者大于1的数字，默认0不做判断<br/>\
                                            注：满标（即最后一名）填写-1')
    msg_template = models.TextField(u'站内信模板（不填则不发）', blank=True,
                                    help_text=u'站内信模板不填写则触发该规则时不发站内信，变量写在2个大括号之间，<br/>\
                                              内置：注册人手机：“{{mobile}}，奖品激活码：{{reward}}，截止日期{{end_date}}<br/>\
                                              邀请人：{{inviter}}，被邀请人：{{invited}}，赠送金额/比率{{income}}<br/>\
                                              活动名称：{{name}}，红包最高抵扣金额：{{highest_amount}}，充值/投资金额{{amount}}<br/>\
                                              优惠券金额/百分比：{{redpack_amount}}，优惠券投资门槛：{{invest_amount}}”')
    sms_template = models.TextField(u'短信模板（不填则不发）', blank=True,
                                    help_text=u'短信模板不填写则触发该规则时不发手机短信，变量写在2个大括号之间，变量：同上')

    wx_template = models.CharField(u'微信消息模板', blank=True,
                                    choices=WX_TEMPLATE_CHOICE, default="", max_length=32)

    msg_template_introduce = models.TextField(u'邀请人站内信模板', blank=True,
                                              help_text=u'邀请人站内信模板不填写则不发送，变量写在2个大括号之间，变量：同上')
    sms_template_introduce = models.TextField(u'邀请人短信模板', blank=True,
                                              help_text=u'邀请人短信模板不填写则不发送，变量写在2个大括号之间，变量：同上')
    send_type = models.CharField(u'赠送发放方式', max_length=20, choices=SEND_TYPE,
                                 default=u'系统实时发放')
    created_at = models.DateTimeField(auto_now=True, default=timezone.now)
    is_used = models.BooleanField(u'是否启用', default=False)

    def __unicode__(self):
        return self.rule_name

    class Meta:
        verbose_name_plural = u'活动规则'

    def clean(self):
        if self.gift_type == 'reward' and not self.reward:
            raise ValidationError(u'赠送类型为“奖品”时，必须填写“奖品类型名称”')
        if (self.gift_type == 'redpack' or self.gift_type == 'experience_gold') and not self.redpack:
            raise ValidationError(u'赠送类型为“优惠券/体验金”时，必须填写“对应活动ID”')
        if self.gift_type == 'income' or self.gift_type == 'phonefare':
            if self.income <= 0:
                raise ValidationError(u'选择送收益或手机话费时要填写“金额或比率”')
        if self.min_amount > 0 and self.max_amount > 0:
            if self.min_amount >= self.max_amount:
                raise ValidationError(u'最小金额和最大金额都大于0时，最大金额必须大于最小金额')
        if self.total_invest_order > 0 and not self.is_total_invest:
            raise ValidationError(u'当设置累计投资名次时必须勾选“启用满标累计投资”')


class ActivityRecord(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=u'活动名称')
    rule = models.ForeignKey(ActivityRule, verbose_name=u'规则名称')
    platform = models.CharField(u'平台', max_length=20)
    trigger_node = models.CharField(u'触发节点', max_length=20, choices=TRIGGER_NODE)
    trigger_at = models.DateTimeField(u'触发时间', auto_created=False)
    description = models.TextField(u'摘要', blank=True)
    msg_type = models.CharField(u'信息类型', max_length=20, choices=MSG_TYPE, default=u"只记录")
    send_type = models.CharField(u'发放方式', max_length=20, choices=SEND_TYPE_ABBR, default=u'系统')
    gift_type = models.CharField(u'赠送类型', max_length=20, choices=GIFT_TYPE, default='')
    user = models.ForeignKey(User, verbose_name=u"触发用户")
    income = models.FloatField(u'费用或收益', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, default=timezone.now, db_index=True)

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

    img_type = models.CharField(max_length=20, choices=IMG_TYPE, default='reward', verbose_name=u'图片类别')
    name = models.CharField(max_length=128, verbose_name=u'图片名称', help_text=u'当图片类别是元素时,模板中会显示')
    img = models.ImageField(upload_to='activity', blank=True, verbose_name=u'图片')
    desc_one = models.TextField(blank=True, verbose_name=u'图片描述1', help_text=u'展示在图片旁边的描述信息，当此项是奖品图片的描述或者自定义图片的描述信息时，需要信息换行时，在行结尾结尾添加符号：|*|')
    desc_two = models.TextField(blank=True, verbose_name=u'图片描述2', help_text=u'展示在图片旁边的描述信息')
    priority = models.IntegerField(verbose_name=u'优先级', default=0, help_text=u'越大越优先')
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

    TEACHER_CHOICE = (
        (0, u'关闭此模块'),
        (1, u'加载第一种默认样式'),
        (2, u'加载第二种默认样式'),
    )

    REWARD_CHOICE = (
        (0, u'关闭此模块'),
        (1, u'加载第一种默认样式'),
        (2, u'加载第二种默认样式'),
        (3, u'自定义第一种样式'),
        (4, u'自定义第二种样式'),
    )

    TEXT_LOCATION_CHOICE = (
        (0, u'靠左'),
        (1, u'居中'),
        (2, u'靠右'),
    )

    name = models.CharField(u'活动名称', max_length=128, blank=True, help_text=u'例如<活动时间：2015-03-18至2015-03-28>')
    # logo
    logo = models.ImageField(u'网利宝logo图片', null=True, upload_to='activity', blank=True)
    logo_other = models.ImageField(u'第三方logo图片', null=True, upload_to='activity', blank=True)
    location = models.BooleanField(u'是否改变logo顺序', default=False, help_text=u'勾选此项则，则网利宝logo在后，第三方logo在前')
    # banner
    banner = models.ImageField(u'banner图片', null=True, upload_to='activity', blank=True)
    # login
    is_login = models.BooleanField(u'登录入口', default=False, help_text=u'勾选此项则在活动页面加载注册登录入口模块')
    login_invite = models.BooleanField(u'邀请码输入框', default=False, help_text=u'勾选此项则登录窗口允许用户输入邀请码')
    login_desc = models.CharField(u'登录入口标语', max_length=128, blank=True, help_text=u'例如<一句话宣传语>')
    is_login_href = models.BooleanField(u'登录入口是否添加超链接', default=False, help_text=u'勾选此项则在登录入口添加超链接')
    login_href_desc = models.CharField(u'入口超链接描述', max_length=128, blank=True, help_text=u'超连接描述如<【立即领取】>')
    login_href = models.CharField(u'入口超链接', max_length=128, blank=True, help_text=u'添加超链接绝对地址，以http或https开头')
    # 活动时间及描述
    is_activity_desc = models.IntegerField(u'加载活动时间及描述模块方案', max_length=20, choices=OPEN_CHOICE, default=0, help_text=u'当选择加载默认模块时，则加载默认图片，可以自定义活动时间和活动描述')
    desc = models.CharField(u'活动描述', max_length=1024, blank=True, null=True, help_text=u'例如<一句话描述，活动期间怎么怎么滴>')
    desc_time = models.CharField(u'活动时间', max_length=1024, blank=True, null=True, help_text=u'例如<活动时间：2015-03-18至2015-03-28>')
    desc_img = models.CharField(u'活动图片ID:', max_length=60, blank=True, null=True, help_text=u'如果有多个图片，则图片ID之间用英文逗号分割，根据图片ID顺序展示图片')
    # 活动奖品图片及描述
    is_reward = models.IntegerField(u'加载活动奖品模块方案', max_length=20, choices=REWARD_CHOICE, default=0)
    reward_img = models.CharField(u'活动奖品图片ID', max_length=60, blank=True, null=True, help_text=u'如果有多个图片，则图片ID之间用英文逗号分割，根据图片ID顺序展示图片')
    reward_desc = models.TextField(u'自定义第二种样式活动描述', blank=True, null=True, help_text=u'当自定义第二种样式时，需要填写词描述，例如<活动期间，单日投资额达到以下额度，可获得相应奖品。>')
    # 好友邀请及描述
    is_introduce = models.IntegerField(u'加载邀请好友模块方案', max_length=20, choices=OPEN_CHOICE, default=0, help_text=u'当选择加载自定义设置时，自定义内容才会被加载到模板中')
    introduce_img = models.ImageField(u'邀请好友图片:', blank=True, null=True, upload_to='activity')
    # 新手投资流程
    is_teacher = models.IntegerField(u'加载活动奖品模块方案', max_length=20, choices=TEACHER_CHOICE, default=0)
    teacher_desc = models.CharField(
        u'自定义描述', max_length=1024, blank=True, null=True, default=' |*| |*| |*| |*| ',
        help_text=u'如果新手新手投资流程对应的步骤有自定义描述，在此处添加，描述使用|*|分割。例如在第1、2、4步骤下添加注释，则<描述1|*|描述2|*||*|描述4|*|>')
    # 活动规则
    is_rule_use = models.IntegerField(u'加载活动使用规则模块方案', max_length=20, choices=OPEN_CHOICE, default=0)
    rule_use_name = models.CharField(u'重命名规则名称', max_length='128', null=True, blank=True, help_text=u'填写此项则更改规则名称')
    rule_use = models.TextField(u'使用规则', blank=True, null=True, help_text=u'每一条规则结尾使用|*|分割。例如在第1、2、4步骤下添加注释，则<规则1|*|规则2|*|规则3>')
    # 使用规则
    is_rule_activity = models.IntegerField(u'加载活动规则模块方案', max_length=20, choices=OPEN_CHOICE, default=0)
    rule_activity_name = models.CharField(u'重命名规则名称', max_length='128', null=True, blank=True, help_text=u'填写此项则更改规则名称')
    rule_activity = models.TextField(u'活动规则', blank=True, null=True, help_text=u'每一条规则结尾使用|*|分割。例如在第1、2、4步骤下添加注释，则<规则1|*|规则2|*|规则3>')
    # 奖品发放规则
    is_rule_reward = models.IntegerField(u'加载奖品发放规则模块方案', max_length=20, choices=OPEN_CHOICE, default=0)
    rule_reward_name = models.CharField(u'重命名规则名称', max_length='128', null=True, blank=True, help_text=u'填写此项则更改规则名称')
    rule_reward = models.TextField(u'奖品发放', blank=True, null=True, help_text=u'每一条规则结尾使用|*|分割。例如在第1、2、4步骤下添加注释，则<规则1|*|规则2|*|规则3>')
    # 底部模块
    is_footer = models.IntegerField(u'底部背景颜色模块', max_length=20, choices=OPEN_CHOICE, default=0)
    footer_color = models.CharField(u'自定义底部背景颜色', max_length=20, null=True, blank=True, help_text=u'自定义底部背景颜色，如<#A70DC0>')
    # 高收益柱形图
    is_earning_one = models.BooleanField(u'高收益柱形图介绍模块', default=False, help_text=u'勾选此项则在活动页面加载高收益柱形图模块')
    # 多种选择介绍
    is_earning_two = models.BooleanField(u'多种选择介绍模块', default=False, help_text=u'勾选此项则在活动页面加载多种选择介绍模块模块')
    # 投资奖励活动介绍
    is_earning_three = models.BooleanField(u'活动投资奖励模块', default=False, help_text=u'勾选此项则在活动页面加载活动投资奖励模块')
    # 添加波浪背景模块
    is_background = models.IntegerField(u'加载背景图模块方案', max_length=20, choices=OPEN_CHOICE, default=0, help_text=u'默认方案为使用默认背景图片，自定义方案为自定义背景图片')
    background_img = models.ImageField(u'自定义背景图片:', blank=True, null=True, upload_to='activity')
    background_location = models.CharField(u'背景图片位置', max_length=20, null=True, blank=True, help_text=u'填写要添加背景图片的模块序号，此项只允许填写一个模块序号')
    # 选择显示模板顺序
    models_sequence = models.CharField(u'填写展示模块的顺序', max_length=60, null=False, blank=True, help_text=u'根据各个模块的编号填写加载各个模块的顺序，头部、banner和底部不允许改变，无需填写，序号使用逗号分割，例如<1,2,3,4>')

    # 自定义图片及描述
    is_diy = models.BooleanField(u'自定义图片或描述模块', default=False, help_text=u'勾选此项则活动页面加载自定义图片及描述')
    diy_img = models.CharField(u'自定义图片ID', max_length=20, null=True, blank=True, help_text=u'在模板图片根据ID查找，<br /> 1、存在图片和描述，则加载图片和描述 <br /> 2、如果只有图片没有描述，则只加载图片 <br /> 3、如果只有描述没有图片，则只加载描述')
    diy_location = models.IntegerField(u'自定义描述位置', max_length=20, choices=TEXT_LOCATION_CHOICE, default=0, help_text=u'当自定义图片ID存在描述时，根据此项定位描述位置')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'活动模板'

    def preview_link(self):
        return u'<a href="/templates/zero/%s/" target="_blank">预览</a>' % str(self.id)
    preview_link.short_description = u'预览'
    preview_link.allow_tags = True


class WapActivityTemplates(models.Model):
    """ 管理wap活动页面 """
    name = models.CharField(u"名称", max_length=60, blank=True)
    url = models.CharField(u"活动URL地址", max_length=128, blank=True, null=True)
    aim_template = models.CharField(u"目的模板名称", max_length=60, blank=True, null=True)
    is_rendering = models.BooleanField(u'是否使用函数渲染模板', default=False)
    func_rendering = models.CharField(
        u'渲染模板的函数名称', max_length=60, null=True, blank=True,
        help_text=u'填写函数名称，如需要使用 rendering_func(*args, **kwargs)，则填写 rendering_func函数名')
    start_at = models.DateTimeField(u"活动开始时间*", default=timezone.now, null=False)
    end_at = models.DateTimeField(u"活动结束时间*", default=timezone.now, null=False)
    created_at = models.DateTimeField(auto_now=True, default=timezone.now)
    is_used = models.BooleanField(u'是否启用', default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'活动页跳转管理功能'


class ActivityShow(models.Model):
    """活动展示"""
    ACTIVITY_CATEGORY = (
        ('all', u'全部'),
        ('purchase', u'投资有奖'),
        ('holiday', u'节日热点'),
        ('novice', u'新手福利'),
    )

    activity = models.ForeignKey(Activity, verbose_name=u'活动名称')
    category = models.CharField(u'活动类型', max_length=20, choices=ACTIVITY_CATEGORY, default=u'全部')
    is_pc = models.BooleanField(u'是否主站活动', default=False)
    thumbnail = models.ImageField(u'卡片区域缩略图', null=True, blank=True, upload_to='activity')
    pc_detail_link = models.CharField(u'PC-活动详情页链接*', null=True, blank=True, max_length=255)
    pc_template = models.CharField(u'PC-活动详情页模板名称*', null=True, blank=True, max_length=255)
    pc_description = models.TextField(u'PC-活动简介', null=True, blank=True)
    is_app = models.BooleanField(u'是否APP活动', default=False)
    app_banner = models.ImageField(u'APP-活动Banner', null=True, blank=True, upload_to='activity')
    app_detail_link = models.CharField(u'APP-活动详情页链接*', null=True, blank=True, max_length=255)
    app_template = models.CharField(u'APP-活动详情页模板名称*', null=True, blank=True, max_length=255)
    app_description = models.TextField(u'APP-活动简介', null=True, blank=True)
    start_at = models.DateTimeField(u"页面展示开始时间*", auto_now=False, default=timezone.now, null=False)
    end_at = models.DateTimeField(u"页面展示结束时间*", auto_now=False, default=timezone.now, null=False)
    created_at = models.DateTimeField(u'添加时间', auto_now=False, default=timezone.now, auto_now_add=True)
    link_is_hide = models.BooleanField(verbose_name=u'是否隐藏活动页面', default=False)
    priority = models.IntegerField(u'优先级', help_text=u'越大越优先', default=0, blank=False)
    main_banner = models.ImageField(u'主推Banner', null=True, blank=True, upload_to='activity/banner')
    left_banner = models.ImageField(u'副推左Banner', null=True, blank=True, upload_to='activity/banner')
    right_banner = models.ImageField(u'副推右Banner', null=True, blank=True, upload_to='activity/banner')

    def activity_status(self):
        now = timezone.now()
        if self.activity.start_at > now:
            return u'未开始'
        elif now > self.activity.end_at:
            return u'已结束'
        elif self.activity.end_at - now <= timedelta(days=1):
            return u'剩%s小时' % ((self.activity.end_at - now).seconds / 3600)
        elif self.activity.end_at - now <= timedelta(days=7):
            return u'剩%s天' % (self.activity.end_at - now).days
        elif self.activity.end_at - now > timedelta(days=7):
            return u'进行中'

    activity_status.short_description = u'活动状态'
    activity_status.allow_tags = True

    def platform(self):
        return self.activity.platform

    platform.short_description = u'活动平台'
    platform.allow_tags = True

    def channel(self):
        return self.activity.channel

    channel.short_description = u'渠道'
    channel.allow_tags = True

    def save(self, *args, **kwargs):
        if self.is_pc is False:
            self.thumbnail = None
            self.pc_detail_link = None
            self.pc_template = None
            self.pc_description = None

        if self.is_app is False:
            self.app_banner = None
            self.app_detail_link = None
            self.app_template = None
            self.app_description = None

        super(ActivityShow, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.activity.name

    class Meta:
        verbose_name = u'活动页管理'
        verbose_name_plural = u'活动页管理'
        ordering = ['-priority', '-created_at']


class ActivityBannerPosition(models.Model):
    """PC-活动Banner展示位置"""
    main = models.ForeignKey(ActivityShow, verbose_name=u'主推', related_name='act_banner_main')
    main_banner = models.ImageField(u'主推Banner', null=True, blank=True, upload_to='activity')
    second_left = models.ForeignKey(ActivityShow, verbose_name=u'副推左', related_name='act_banner_left')
    left_banner = models.ImageField(u'副推左Banner', null=True, blank=True, upload_to='activity')
    second_right = models.ForeignKey(ActivityShow, verbose_name=u'副推右', related_name='act_banner_right')
    right_banner = models.ImageField(u'副推右Banner', null=True, blank=True, upload_to='activity')
    priority = models.IntegerField(u'优先级', help_text=u'越大越优先', default=0, blank=False)
    created_at = models.DateTimeField(u'创建时间', auto_now=False, default=timezone.now, auto_now_add=True)

    class Meta:
        verbose_name = u'活动Banner展示位置'
        verbose_name_plural = u'活动Banner展示位置'
        ordering = ['-priority', '-created_at']

    def __unicode__(self):
        return u'（主推）：%s——（副推左）：%s——（副推右）：%s' % (self.main.activity.name,
                                                            self.second_left.activity.name,
                                                            self.second_right.activity.name,
                                                            )


class ActivityBannerShow(models.Model):
    """活动Banner展示排期"""

    BANNER_TYPE = (
        (u'主推', u'主推'),
        (u'副推左', u'副推左'),
        (u'副推右', u'副推右'),
    )

    activity_show = models.ForeignKey(ActivityShow, verbose_name=u'活动展示')
    banner_type = models.CharField(u'Banner类型', max_length=10, choices=BANNER_TYPE)
    show_start_at = models.DateTimeField(u'Banner展示开始时间', auto_now=False, default=timezone.now,
                                         help_text=u'大于等于『活动展示』开始时间')
    show_end_at = models.DateTimeField(u'Banner展示结束时间', auto_now=False, default=timezone.now,
                                       help_text=u'小于等于『活动展示』结束时间')
    created_at = models.DateTimeField(u'创建时间', auto_now=True)

    class Meta:
        verbose_name = u'活动Banner展示排期'
        verbose_name_plural = u'活动Banner展示排期'
        ordering = ['-show_start_at']

    def __unicode__(self):
        return u'%s(%s)' % (self.activity_show.activity, self.banner_type)
