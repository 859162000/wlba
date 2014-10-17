# encoding: utf-8
from django.db import models


class Announcement(models.Model):
    DEVICES = (
        ('pc', u'PC端'),
        ('mobile', u'手机端'),
    )
    TYPES = (
        ('homepage', u'首页'),
        ('fund', u'基金页面'),
        ('trust', u'信托页面'),
        ('accounts', u'账户中心'),
        ('all', u'所有页面')
    )
    STATUS = (
        (0, u'未审核'),
        (1, u'已审核')
    )
    device = models.CharField(max_length=15, verbose_name=u'设备', default='pc', choices=DEVICES, help_text=u'目标设备 PC 或 mobile')
    type = models.CharField(max_length=15, verbose_name=u'类型', choices=TYPES, default='all', help_text=u'类型 首页 基金 信托 账户中心 所有页面')
    title = models.CharField(max_length=100, verbose_name=u'公告名称', help_text=u'公告名称')
    content = models.TextField(verbose_name=u'公告内容', help_text=u'公告内容')
    priority = models.IntegerField(blank=True, default=0, verbose_name=u'优先级', help_text=u'越大越优先')
    starttime = models.DateTimeField(auto_now=False, verbose_name=u'开始时间', help_text=u'开始时间')
    endtime = models.DateTimeField(auto_now=False, verbose_name=u'结束时间', help_text=u'结束时间')
    status = models.SmallIntegerField(verbose_name=u'审核状态', help_text=u'审核状态', max_length=2, choices=STATUS, default=0)
    updatetime = models.DateTimeField(auto_now=True, verbose_name=u'更新时间', help_text=u'更新时间')

    class Meta:
        verbose_name_plural = u'公告'
        ordering = ['-priority', '-updatetime']

    def __unicode__(self):
        return "%s" % self.title