# encoding: utf-8

import logging
from concurrency.fields import IntegerVersionField
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)


class P2PProduct(models.Model):
    version = IntegerVersionField()
    category = models.CharField(max_length=16, default=u'普通', verbose_name=u'产品类别*')
    types = models.CharField(u"产品分类(新)", max_length=50, null=True)
    name = models.CharField(max_length=256, verbose_name=u'名字*', blank=False)
    short_name = models.CharField(verbose_name=u'短名字*', max_length=64, blank=False, help_text=u'短名字要求不超过13个字')
    serial_number = models.CharField(verbose_name=u'产品编号*', max_length=100, unique=True, blank=False, null=True)
    status = models.CharField(u'产品状态*', max_length=16, default=u'录标', db_index=True)
    period = models.IntegerField(default=0, verbose_name=u'产品期限(月/天)*', blank=False)
    brief = models.TextField(blank=True, verbose_name=u'产品备注')
    expected_earning_rate = models.FloatField(default=0, verbose_name=u'预期收益(%)*', blank=False)
    excess_earning_rate = models.FloatField(default=0, verbose_name=u'超额收益(%)*')
    excess_earning_description = models.CharField(u'超额收益描述', max_length=100, blank=True, null=True)

    pay_method = models.CharField(u'还款方式*', max_length=32, blank=False, default=u'等额本息')
    amortization_count = models.IntegerField(u'还款期数', default=0)
    repaying_source = models.TextField(verbose_name=u'还款资金来源(合同用)', blank=True)

    total_amount = models.BigIntegerField(default=1, verbose_name=u'借款总额*', blank=False)
    ordered_amount = models.BigIntegerField(default=0, verbose_name=u'已募集金额*')

    publish_time = models.DateTimeField(default=lambda: timezone.now() + timezone.timedelta(days=10), verbose_name=u'发布时间*', blank=False, db_index=True)
    end_time = models.DateTimeField(default=lambda: timezone.now() + timezone.timedelta(days=20), verbose_name=u'终止时间*', blank=False)
    soldout_time = models.DateTimeField(u'售完时间', null=True, blank=True, db_index=True)

    make_loans_time = models.DateTimeField(u'放款时间', null=True, blank=True)

    limit_per_user = models.FloatField(verbose_name=u'单用户购买限额(0-1的系数)*', default=1)

    class Meta:
        verbose_name_plural = u'P2P产品'

    def __unicode__(self):
        return u'%s<%s>' % (self.id,self.name)


class P2PRecord(models.Model):
    catalog = models.CharField(u'流水类型', max_length=100, db_index=True)
    order_id = models.IntegerField(u'关联订单编号', null=True, db_index=True)
    amount = models.DecimalField(u'发生数', max_digits=20, decimal_places=2)

    product = models.ForeignKey(P2PProduct, help_text=u'标的产品', null=True, on_delete=models.SET_NULL)
    product_balance_after = models.IntegerField(u'标的后余额', help_text=u'该笔流水发生后标的剩余量', null=True)

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    create_time = models.DateTimeField(u'发生时间', auto_now_add=True)

    description = models.CharField(u'摘要', default='', max_length=1000)

    platform = models.CharField(u'购买平台', max_length=100, default=u'手动投标')

    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'产品流水'

    def __unicode__(self):
        return u'流水号%s %s 发生金额%s' % (self.id, self.catalog, self.amount)
