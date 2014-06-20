# encoding: utf-8
import collections
from decimal import Decimal
from django.db import models
from django.db.models import F
from django.utils import timezone
from jsonfield import JSONField
from wanglibao.models import ProductBase
from django.contrib.auth import get_user_model
from utility import gen_hash_list

user_model = get_user_model()


class WarrantCompany(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'名字')

    def __unicode__(self):
        return u'%s' % self.name



class P2PProductManager(models.Manager):
    def get_queryset(self):
        return super(P2PProductManager, self).get_queryset().filter(total_amount__exact=F('ordered_amount'),
                                                                    status__exact=u'正在招标')


class P2PProductPayment(models.Model):
    name = models.CharField(max_length=255, verbose_name=u'付款方式')
    description = models.CharField(max_length=1000, verbose_name=u'描述', blank=u'', default=u'')

    catalog_id = models.IntegerField(verbose_name=u'类别ID')

    def __unicode__(self):
        return u'%s, id:%s' % (self.name, self.catalog_id)


class P2PProduct(ProductBase):
    name = models.CharField(max_length=256, verbose_name=u'名字')
    short_name = models.CharField(max_length=64, verbose_name=u'短名字')

    status = models.CharField(max_length=16, default=u'正在招标', verbose_name=u'产品装态(正在招标，已满标，还款中)')

    period = models.IntegerField(default=0, verbose_name=u'产品期限(月)')
    brief = models.TextField(blank=True, verbose_name=u'产品点评')
    expected_earning_rate = models.FloatField(default=0, verbose_name=u'预期收益(%)')
    closed = models.BooleanField(verbose_name=u'是否完结', default=False)

    payment = models.ForeignKey(P2PProductPayment, null=True)

    total_amount = models.BigIntegerField(default=0, verbose_name=u'借款总额')
    ordered_amount = models.BigIntegerField(default=0, verbose_name=u'已募集金额')

    extra_data = JSONField(blank=True, load_kwargs={'object_pairs_hook': collections.OrderedDict})

    publish_time = models.DateTimeField(default=timezone.now, verbose_name=u'发布时间')
    end_time = models.DateTimeField(default=timezone.now, verbose_name=u'终止时间')

    limit_per_user = models.FloatField(verbose_name=u'单用户购买限额', default=0.2)

    warrant_company = models.ForeignKey(WarrantCompany)
    usage = models.TextField(blank=True, verbose_name=u'项目用途')
    short_usage = models.TextField(blank=True, verbose_name=u'项目用途摘要')

    objects = models.Manager()
    sold_out = P2PProductManager()

    def __unicode__(self):
        return u'<%s %f, 总量: %s, 已募集: %s, 完成率: %s %%>' % (self.name, self.expected_earning_rate, self.total_amount,
                                            self.ordered_amount, self.completion_rate)

    @property
    def remain(self):
        return self.total_amount - self.ordered_amount

    @property
    def completion_rate(self):
        if not self.total_amount > 0:
            return 0
        return float(self.ordered_amount) / float(self.total_amount) * 100

    @property
    def limit_amount_per_user(self):
        return int(self.limit_per_user * self.total_amount)

    def has_amount(self, amount):
        if amount <= self.remain:
            return True
        return False


class Warrant(models.Model):
    name = models.CharField(max_length=16, verbose_name=u'名字')
    warranted_at = models.DateTimeField(default=timezone.now, verbose_name=u'认证时间')
    created_at = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')

    product = models.ForeignKey(P2PProduct)

    def __unicode__(self):
        return u'%s %s %s' % (self.product.name, self.name, str(self.warranted_at))


class ProductAmortization(models.Model):
    product = models.ForeignKey(P2PProduct, related_name='amortizations')

    term = models.IntegerField(verbose_name=u'还款期数')
    amount = models.DecimalField(verbose_name=u'应付款项', max_digits=20, decimal_places=2)
    penal_interest = models.DecimalField(verbose_name=u'额外罚息', max_digits=20, decimal_places=2, default=Decimal('0'))
    delay = models.IntegerField(verbose_name=u'逾期天数', default=0)

    comment = models.CharField(verbose_name=u'摘要', max_length=500)
    settled = models.BooleanField(verbose_name=u'已结算给客户')
    settlement_time = models.DateTimeField(verbose_name=u'结算时间')

    created_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    @property
    def total_amount(self):
        return self.amount + self.penal_interest

    def __unicode__(self):
        return u'产品<%s>: 第 %s 期，总额 %s 元' % (self.product.short_name, self.term, self.amount)


class ProductUserAmortization(models.Model):
    amortization = models.ForeignKey(ProductAmortization, related_name=u'to_users')
    user = models.ForeignKey(get_user_model())
    created_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    current_equity = models.BigIntegerField(verbose_name=u'分配时点用户所持份额')
    amount = models.DecimalField(verbose_name=u'还款金额', max_digits=20, decimal_places=2)
    description = models.CharField(verbose_name=u'摘要', max_length=1000)

    def __unicode__(self):
        return u'用户 %s 产品 %s 还款 %s'


class P2PRecord(models.Model):
    catalog = models.CharField(verbose_name=u'流水类型', max_length=100)
    order_id = models.IntegerField(verbose_name=u'关联订单编号')
    amount = models.DecimalField(verbose_name=u'发生数', max_digits=20, decimal_places=2)

    product = models.ForeignKey(P2PProduct, help_text=u'标的产品', null=True)
    product_balance_after = models.IntegerField(verbose_name=u'标的后余额', help_text=u'该笔流水发生后标的剩余量', null=True)

    user = models.ForeignKey(get_user_model(), null=True)

    create_time = models.DateTimeField(verbose_name=u'发生时间', auto_now_add=True)

    description = models.CharField(verbose_name=u'摘要', default='', max_length=1000)

    class Meta:
        ordering = ['-create_time']

    def __unicode__(self):
        return u'流水号%s %s 发生金额%s' %(self.id, self.catalog, self.amount)


class P2PEquity(models.Model):
    user = models.ForeignKey(get_user_model(), related_name='equities')
    product = models.ForeignKey(P2PProduct, help_text=u'产品', related_name='equities')
    equity = models.BigIntegerField(verbose_name=u'用户所持份额', default=0)
    confirm = models.BooleanField(verbose_name=u'确认成功', default=False)

    class Meta:
        unique_together = (('user', 'product'),)

    def __unicode__(self):
        return u'%s 持有 %s 数量:%s' % (self.user, self.product, self.equity)

    @property
    def related_orders(self):
        records = list()
        return records

    @property
    def ratio(self):
        return float(self.equity) / float(self.product.total_amount)


class EquityRecord(models.Model):
    catalog = models.CharField(verbose_name=u'流水类型', max_length=100)
    user = models.ForeignKey(get_user_model())
    product = models.ForeignKey(P2PProduct, verbose_name=u'产品')
    amount = models.DecimalField(verbose_name=u'发生数量', max_digits=20, decimal_places=2)
    description = models.CharField(verbose_name=u'摘要', max_length=1000, default=u'')

    checksum = models.CharField(verbose_name=u'签名', default=u'', max_length=1000)
    create_time = models.DateTimeField(verbose_name=u'流水时间', auto_now_add=True)

    def __unicode__(self):
        return u'%s %s %s %s' %(self.catalog, self.user, self.product, self.amount)
