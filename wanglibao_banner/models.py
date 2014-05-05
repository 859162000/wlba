# encoding: utf-8
from django.db import models
import time


class Banner(models.Model):
    MOBILE = 'mobile'
    PC = 'PC'
    DEVICES = (
        (MOBILE, MOBILE),
        (PC, PC)
    )

    TYPES = (
        ('fund', 'fund'),
        ('trust', 'trust'),
        ('banner', 'banner'),
        ('ad', 'ad')
    )
    device = models.CharField(max_length=15, verbose_name=u'设备', choices=DEVICES)
    type = models.CharField(max_length=15, verbose_name=u'类型', choices=TYPES)
    name = models.CharField(max_length=30, verbose_name=u'名称')
    link = models.URLField(max_length=1024, blank=True, verbose_name='link')
    image = models.ImageField(upload_to='banner', blank=True, verbose_name=u'图片')
    priority = models.IntegerField(verbose_name=u'优先级', help_text=u'越大越优先')
    alt = models.TextField(blank=True, verbose_name=u'图片说明')
    last_updated = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')