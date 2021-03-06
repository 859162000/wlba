# encoding: utf-8
from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField


class Announcement(models.Model):
    DEVICES = (
        ('pc', u'PC端'),
        ('mobile', u'手机端'),
        ('pc&app', u'PC+APP')
    )
    TYPES = (
        ('homepage', u'首页'),
        ('p2p', u'p2p页面'),
        ('p2pnew', u'p2p新标'),
        ('fund', u'基金页面'),
        ('trust', u'信托页面'),
        ('accounts', u'用户账户中心'),
        ('all', u'所有页面')
    )
    STATUS = (
        (0, u'未审核'),
        (1, u'已审核')
    )
    device = models.CharField(max_length=15, verbose_name=u'设备', default='pc', choices=DEVICES, help_text=u'目标设备 PC 或 mobile')
    type = models.CharField(max_length=15, blank=True, null=True, verbose_name=u'展示位置', choices=TYPES, help_text=u'公告区块的展示位置（页面横条公告）')
    title = models.CharField(max_length=100, verbose_name=u'公告名称', help_text=u'公告名称')
    content = RichTextField()
    priority = models.IntegerField(blank=True, default=0, verbose_name=u'优先级', help_text=u'越大越优先')
    hideinlist = models.BooleanField(verbose_name=u'是否隐藏（公告列表页面）', default=False)
    starttime = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=u'展示开始时间', help_text=u'展示开始时间')
    endtime = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=u'展示结束时间', help_text=u'展示结束时间')
    status = models.SmallIntegerField(verbose_name=u'审核状态', help_text=u'审核状态', max_length=2, choices=STATUS, default=0)
    createtime = models.DateTimeField(auto_now=False, default=timezone.now, verbose_name=u'发布时间', help_text=u'发布时间')
    updatetime = models.DateTimeField(auto_now=True, verbose_name=u'更新时间', help_text=u'更新时间')
    page_title = models.CharField(max_length=100, verbose_name=u'公告页面标题', blank=True, null=True, help_text=u'公告页面标题')

    class Meta:
        verbose_name_plural = u'公告'
        ordering = ['-createtime']

    def __unicode__(self):
        return "%s" % self.title

    def preview_link(self):
        return u'<a href="/announcement/preview/%s" target="_blank">预览</a>' % str(self.id)
    preview_link.short_description = u'预览'
    preview_link.allow_tags = True

    def get_absolute_url(self):
        return '/announcement/detail/%s' % self.id


class AppMemorabilia(models.Model):
    STATUS = (
        (0, u'未进行'),
        (1, u'进行中')
    )

    title = models.CharField(max_length=100, blank=False, null=False, verbose_name=u'名称')
    banner = models.ImageField(upload_to='announcement', blank=False, null=False, verbose_name=u'Banner')
    content = RichTextField()
    detail_link = models.CharField(u'是否指定详情页链接', max_length=255, blank=True, null=True,
                                   help_text=u'如：https://www.wanglibao.com')
    done_date = models.DateField(auto_now=False, default=timezone.now, verbose_name=u'完成日期')
    start_time = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=u'展示开始时间')
    end_time = models.DateTimeField(auto_now=False, blank=True, null=True, verbose_name=u'展示结束时间')
    priority = models.IntegerField(blank=True, default=0, verbose_name=u'优先级', help_text=u'越大越优先')
    status = models.SmallIntegerField(verbose_name=u'当前状态', max_length=2, choices=STATUS, default=0)
    hide_link = models.BooleanField(verbose_name=u'是否隐藏（大事记页面）', default=False)
    created_time = models.DateTimeField(u'发布时间', auto_now_add=True, default=timezone.now())
    updated_time = models.DateTimeField(u'更新时间', auto_now=True, default=timezone.now())
    page_title = models.CharField(max_length=100, verbose_name=u'大事记页面标题', blank=True, null=True)

    class Meta:
        verbose_name = u"APP-大事记"
        verbose_name_plural = u'APP-大事记'
        ordering = ['-priority']

    def __unicode__(self):
        return "%s" % self.title

    def get_absolute_url(self):
        if self.detail_link:
            return self.detail_link
        else:
            return '/app/memorabilia/detail/%s/' % self.id
