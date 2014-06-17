# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models


class PayInfo(models.Model):
    type = models.CharField(verbose_name=u'类型', help_text=u'充值：D 取款：W', max_length=5)
    amount = models.FloatField(verbose_name=u'金额')
    user = models.ForeignKey(get_user_model())


class Bank(models.Model):
    name = models.CharField(verbose_name=u'银行', max_length=32)
    gate_id = models.CharField(max_length=8, verbose_name=u'gate id')
    code = models.CharField(max_length=16, verbose_name=u'银行代码')
    limit = models.TextField(blank=True, verbose_name=u'银行限额信息')
    logo = models.ImageField(upload_to='bank_logo', null=True, blank=True, help_text=u'银行图标')
    sort_order = models.IntegerField(default=0, verbose_name=u'排序权值 从大到小')

    class Meta:
        ordering = '-sort_order',

    def __unicode__(self):
        return u'%s' % self.name
