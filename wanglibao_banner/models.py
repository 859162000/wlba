# encoding: utf-8
from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError


class Banner(models.Model):
    class Meta:
        ordering = ['-priority', '-last_updated']

    MOBILE = 'mobile'
    PC = 'PC'
    PC_2 = 'PC_2'
    WEIXIN = 'weixin'
    DEVICES = (
        (MOBILE, MOBILE),
        (PC, PC),
        (PC_2, PC_2),
        (WEIXIN, WEIXIN),
    )

    TYPES = (
        ('p2p', 'p2p'),
        ('fund', 'fund'),
        ('trust', 'trust'),
        ('banner', 'banner'),
        ('ad', 'ad')
    )
    device = models.CharField(max_length=15, verbose_name=u'设备', choices=DEVICES, help_text=u'目标设备 PC 或 mobile')
    type = models.CharField(max_length=15, verbose_name=u'类型', choices=TYPES, help_text=u'类型 fund trust banner ad')
    name = models.CharField(max_length=30, verbose_name=u'名称', help_text=u'名称')
    link = models.CharField(max_length=1024, blank=True, verbose_name=u'数据', help_text=u'数据 事先约定格式')
    image = models.ImageField(upload_to='banner', blank=True, verbose_name=u'图片', help_text=u'图片')
    priority = models.IntegerField(verbose_name=u'优先级', help_text=u'越大越优先')
    alt = models.TextField(blank=True, verbose_name=u'图片说明', help_text=u'图片说明')
    last_updated = models.DateTimeField(auto_now=True, verbose_name=u'更新时间', help_text=u'上次更新时间')
    is_long_used = models.BooleanField(u'是否长期生效', default=True, help_text=u'默认banner长期有效，如果【不勾选】此项，则需要配置生效时间和失效时间')
    start_at = models.DateTimeField(u"banner生效时间", null=True, blank=True)
    end_at = models.DateTimeField(u"banner失效时间", null=True, blank=True)
    is_used = models.BooleanField(u'是否启用', default=True, help_text=u'默认启用')

    def clean(self):
        if not self.is_long_used:
            if not self.start_at or not self.end_at:
                raise ValidationError(u'如果取消banner长期有效，必须输入banner生效时间和失效时间')


class Partner(models.Model):
    class Meta:
        verbose_name_plural = u'合作伙伴'
        ordering = ['-priority', '-last_updated']

    TYPES = (
        ('partner', u'合作伙伴'),
        ('links', u'友情链接')
    )

    type = models.CharField(max_length=15, verbose_name=u'类型', choices=TYPES, help_text=u'图片类型')
    name = models.CharField(max_length=30, verbose_name=u'名称', help_text=u'图片名称')
    link = models.CharField(max_length=200, blank=True, verbose_name=u'链接网址', default=u'http://', help_text=u'链接网址，需要以http://开头')
    image = models.ImageField(upload_to='banner', blank=True, verbose_name=u'图片', help_text=u'图片，高度40px最佳')
    alt = models.TextField(blank=True, verbose_name=u'图片说明', help_text=u'图片说明')
    priority = models.IntegerField(verbose_name=u'优先级', help_text=u'越大越优先')
    last_updated = models.DateTimeField(auto_now=True, verbose_name=u'更新时间', help_text=u'上次更新时间')

    def __unicode__(self):
        return "%s" % self.name


class Hiring(models.Model):
    TYPES = (
        (u'全部', u'全部'),
        (u'技术类', u'技术类'),
        (u'运营类', u'运营类'),
        (u'产品类', u'产品类'),
    )

    class Meta:
        verbose_name_plural = u'招贤纳士'
        ordering = ['-priority', '-last_updated']

    name = models.CharField(max_length=30, verbose_name=u'岗位名称', help_text=u'岗位名称')
    duties = RichTextField(verbose_name=u'岗位职责')
    requirements = RichTextField(verbose_name=u'任职要求')
    is_urgent = models.BooleanField(verbose_name=u'是否紧急', default=False)
    is_hide = models.BooleanField(verbose_name=u'是否隐藏', default=False)
    priority = models.IntegerField(verbose_name=u'优先级', help_text=u'越大越优先', default=0)
    last_updated = models.DateTimeField(auto_now=True, verbose_name=u'更新时间', help_text=u'更新时间')
    position_types = models.CharField(u'招聘岗位分类', max_length=20, default=u'全部', choices=TYPES)

    def __unicode__(self):
        return "%s" % self.name


class Aboutus(models.Model):
    class Meta:
        verbose_name_plural = u'关于我们'

    title = models.CharField(u'中文标题', max_length=128)
    code = models.CharField(u'英文代码', max_length=30)
    content = RichTextField(verbose_name=u'详细内容')


class AppActivate(models.Model):

    class Meta:
        verbose_name_plural = u'启动页活动(app/pc)'

    DEVICE_TYPE = ('app_iso', 'app_android', 'act_iso', 'act_android', 'act_score_iso', 'pc_home', 'act_i')
    DEVICES = ((x, x) for x in DEVICE_TYPE)
    LINK_CHOICES = (
        (u'1', u'理财专区'),
        (u'2', u'发现页'),
        (u'3', u'全民淘金'),
        (u'4', u'发现页h5页面'),
        (u'5', u'其他h5页面'),
        (u'6', u'体验金'),
    )
    USER_INVEST_LIMIT = (
        (u'-1', u'给所有用户弹出'),
        (u'0', u'给未投资过用户弹出'),
        (u'1', u'给投资过用户弹出'),
    )

    name = models.CharField(u'名称', max_length=30, help_text=u'名称')
    device = models.CharField(u'设备', max_length=15, choices=DEVICES,
                              help_text=u'活动图片应用的设备，启动页选择类型app_*，弹出页选择类型act_*')
    img_one = models.ImageField(u'大图片', upload_to='activity', blank=True,
                                help_text=u'IOS：5.5，Android：1280，图片名称只允许字母数字下划线组成<br/> app端活动弹出框图片地址在此处上传')
    img_two = models.ImageField(u'中图片', upload_to='activity', blank=True,
                                help_text=u'IOS：4.7，Android：720，图片名称只允许字母数字下划线组成')
    img_three = models.ImageField(u'小图片', upload_to='activity', blank=True,
                                  help_text=u'IOS：4.0，Android：480，图片名称只允许字母数字下划线组成')
    img_four = models.ImageField(u'小图片2', upload_to='activity', blank=True,  default='',
                                 help_text=u'IOS：3.5，图片名称只允许字母数字下划线组成，ios使用')
    last_updated = models.DateTimeField(u'更新时间', auto_now=True, help_text=u'上次更新时间')
    is_long_used = models.BooleanField(u'长期生效', default=True,
                                       help_text=u'默认纪录长期有效，如果【不勾选】此项，则需要配置生效时间和失效时间')
    start_at = models.DateTimeField(u"banner生效时间", null=True, blank=True)
    end_at = models.DateTimeField(u"banner失效时间", null=True, blank=True)
    is_used = models.BooleanField(u'是否启用', default=False, help_text=u'默认不启用')
    jump_state = models.BooleanField(u'是否开启跳转', default=False, help_text=u'默认不开启跳转,PC端也适用')
    user_invest_limit = models.CharField(u'用户投资限制', default=u'-1', max_length=8, choices=USER_INVEST_LIMIT, help_text="用户投资限制")
    link_dest = models.CharField(u'跳转链接', default=u'3', max_length=32, choices=LINK_CHOICES)
    link_dest_h5_url = models.CharField(u'活动浮层跳转h5页url', default=u'https://', max_length=300,
                                       help_text=u'如果浮层跳转的是h5页面,一定要配置这个url')
    pc_redirect_url = models.CharField(u'PC端跳转链接', default=u'http://', max_length=300,
                                       help_text=u'PC端跳转链接,请输入http://开头的完整网址')


class AboutDynamic(models.Model):
    title = models.CharField(u'动态标题', max_length=100)
    content = RichTextField()
    priority = models.IntegerField(u'优先级', blank=True, default=0, help_text=u'越大越优先')
    hide_in_list = models.BooleanField(verbose_name=u'是否隐藏（动态列表页面）', default=False)
    start_time = models.DateTimeField(u'展示开始时间', auto_now=False, blank=True, null=True)
    end_time = models.DateTimeField(u'展示结束时间', auto_now=False, blank=True, null=True)
    created_at = models.DateTimeField(u'发布时间', auto_now_add=True)
    updated_time = models.DateTimeField(u'更新时间', auto_now=True)
    description = models.TextField(u'描述', null=True, default='')

    class Meta:
        verbose_name = u'动态'
        verbose_name_plural = u'动态'
        ordering = ['-created_at']

    def __unicode__(self):
        return "%s" % self.title

    def get_absolute_url(self):
        return '/dynamic/detail/%s' % self.id
