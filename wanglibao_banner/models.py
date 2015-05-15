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

    def __unicode__(self):
        return "%s" % self.name


class Aboutus(models.Model):
    class Meta:
        verbose_name_plural = u'关于我们'

    title = models.CharField(u'中文标题', max_length=128)
    code = models.CharField(u'英文代码', max_length=30)
    content = RichTextField(verbose_name=u'详细内容')