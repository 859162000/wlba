# encoding: utf8
import collections
from django.db import models
from django.utils import timezone
from jsonfield import JSONField
from wanglibao.models import ProductBase


class P2PProduct(ProductBase):
    name = models.CharField(max_length=256, verbose_name=u'名字')
    short_name = models.CharField(max_length=64, verbose_name=u'短名字')

    status = models.CharField(max_length=16, default=u'正在招标', verbose_name=u'产品装态(正在招标，已满表，还款中)')

    period = models.IntegerField(default=0, verbose_name=u'产品期限(月)')
    brief = models.TextField(blank=True, verbose_name=u'产品点评')
    expected_earning_rate = models.FloatField(default=0, verbose_name=u'预期收益(%)')

    pay_method = models.CharField(max_length=32, verbose_name=u'还款方式')

    total_amount = models.BigIntegerField(default=0, verbose_name=u'借款总额')
    ordered_amount = models.BigIntegerField(default=0, verbose_name=u'以募集金额')

    extra_data = JSONField(blank=True, load_kwargs={'object_pairs_hook': collections.OrderedDict})

    public_time = models.DateTimeField(default=timezone.now, verbose_name=u'发布时间')
    end_time = models.DateTimeField(default=timezone.now, verbose_name=u'终止时间')

    type = models.CharField(max_length=32, verbose_name=u'产品类型')

    def __unicode__(self):
        return u'%s %f' % (self.name, self.expected_earning_rate)


class Warrant(models.Model):
    name = models.CharField(max_length=16, verbose_name=u'名字')
    warranted_at = models.DateTimeField(default=timezone.now, verbose_name=u'认证时间')
    created_at = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')

    product = models.ForeignKey(P2PProduct)

    def __unicode__(self):
        return u'%s %s %s' % (self.product.name, self.name, str(self.warranted_at))
