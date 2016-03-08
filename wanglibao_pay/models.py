#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from wanglibao_margin.models import MarginRecord


class PayInfo(models.Model):
    """支付记录"""

    type = models.CharField(u'类型', help_text=u'充值：D 取款：W', max_length=5)
    uuid = models.CharField(u'唯一标示', max_length=32, unique=True, db_index=True)
    amount = models.DecimalField(u'实扣金额', max_digits=20, decimal_places=2)
    fee = models.DecimalField(u'手续费', max_digits=20, decimal_places=2, default=0)
    management_fee = models.DecimalField(u'资金管理费用', max_digits=20, decimal_places=2, default=0)
    management_amount = models.DecimalField(u'资金管理金额', max_digits=20, decimal_places=2, default=0)
    total_amount = models.DecimalField(u'总金额', max_digits=20, decimal_places=2, default=0)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    status = models.CharField(u'状态', max_length=15)
    user_id = models.IntegerField(u'用户id', max_length=50)
    order_id = models.IntegerField(u'支付流水号', blank=True, null=True)
    margin_record = models.ForeignKey(MarginRecord, verbose_name=u'账户资金记录', blank=True, null=True)

    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'支付记录'

    def __unicode__(self):
        return u'%s' % self.pk
