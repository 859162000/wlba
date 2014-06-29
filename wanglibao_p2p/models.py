# encoding: utf-8
import collections
from decimal import Decimal
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import get_user_model
from jsonfield import JSONField
from wanglibao.models import ProductBase
from order.models import Order
from utility import gen_hash_list

user_model = get_user_model()


class WarrantCompany(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'名字')

    class Meta:
        verbose_name = u'担保公司'
        verbose_name_plural = u'担保公司'

    def __unicode__(self):
        return u'%s' % self.name


class P2PSoldOutManager(models.Manager):
    def get_queryset(self):
        return super(P2PSoldOutManager, self).get_queryset().filter(total_amount__exact=F('ordered_amount'),
                                                                    status__exact=u'正在招标')


class P2PReadyForSettleManager(models.Manager):
    def get_queryset(self):
        return super(P2PReadyForSettleManager, self).get_queryset().filter(total_amount__exact=F('ordered_amount'),
                                                                           status__exact=u'已满标')


class P2PReadyForFailManager(models.Manager):
    def get_queryset(self):
        return super(P2PReadyForFailManager, self).get_queryset().filter(end_time__lt=timezone.now(),
                                                                         status__exact=u'正在招标')


class P2PProduct(ProductBase):
    STATUS_CHOICES = (
        (u'正在招标', u'正在招标'),
        (u'已满标', u'已满标'),
        (u'还款中', u'还款中')
    )
    name = models.CharField(max_length=256, verbose_name=u'名字')
    short_name = models.CharField(max_length=64, verbose_name=u'短名字')

    status = models.CharField(max_length=16, default=u'正在招标',
                              choices=STATUS_CHOICES,
                              verbose_name=u'产品装态(正在招标，已满标，还款中)')

    period = models.IntegerField(default=0, verbose_name=u'产品期限(月)')
    brief = models.TextField(blank=True, verbose_name=u'产品点评')
    expected_earning_rate = models.FloatField(default=0, verbose_name=u'预期收益(%)')
    closed = models.BooleanField(u'是否完结', default=False)

    pay_method = models.CharField(u'支付方式', max_length=32, blank=True, default=u'等额本息')
    amortization_count = models.IntegerField(u'还款期数', default=0)

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
    sold_out = P2PSoldOutManager()
    ready_for_settle = P2PReadyForSettleManager()
    ready_for_fail = P2PReadyForFailManager()

    class Meta:
        verbose_name_plural = u'P2P产品'

    def __unicode__(self):
        return u'<%s>' % (self.name)

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

    @property
    def current_limit(self):
        return min(self.remain, self.limit_amount_per_user)

    def has_amount(self, amount):
        if amount <= self.remain:
            return True
        return False


class Warrant(models.Model):
    name = models.CharField(max_length=16, verbose_name=u'名字')
    warranted_at = models.DateTimeField(default=timezone.now, verbose_name=u'认证时间')
    created_at = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')

    product = models.ForeignKey(P2PProduct)

    class Meta:
        verbose_name_plural = u'产品担保'

    def __unicode__(self):
        return u'%s %s %s' % (self.product.name, self.name, str(self.warranted_at))


class Attachment(models.Model):
    product = models.ForeignKey(P2PProduct)
    name = models.CharField(u'名字', max_length=128)
    description = models.TextField(u'描述')
    type = models.CharField(u'类型', max_length=32)
    file = models.FileField(upload_to='attachment')
    created_at = models.DateTimeField(auto_now_add=True)
    extra_data = JSONField()

    def __unicode__(self):
        return u'%s' % self.name


class AmortizationReadyManger(models.Manager):
    def get_queryset(self):
        return super(AmortizationReadyManger, self).get_queryset().filter(term_date__lt=timezone.now(),
                                                                          ready_for_settle=True,
                                                                          settled=False)


class ProductAmortization(models.Model):
    product = models.ForeignKey(P2PProduct, related_name='amortizations')

    term = models.IntegerField(verbose_name=u'还款期数')
    term_date = models.DateTimeField(verbose_name=u'还款时间')
    principal = models.DecimalField(verbose_name=u'返还本金', max_digits=20, decimal_places=2)
    interest = models.DecimalField(verbose_name=u'返还利息', max_digits=20, decimal_places=2)
    penal_interest = models.DecimalField(verbose_name=u'额外罚息', max_digits=20, decimal_places=2, default=Decimal('0'))

    settled = models.BooleanField(verbose_name=u'已结算给客户', default=False, editable=False)
    settlement_time = models.DateTimeField(verbose_name=u'结算时间', auto_now=True)

    ready_for_settle = models.BooleanField(verbose_name=u'是否可以开始结算', default=False)

    created_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    description = models.CharField(verbose_name=u'摘要', max_length=500, blank=True)

    objects = models.Manager()
    is_ready = AmortizationReadyManger()

    class Meta:
        verbose_name_plural = u'产品还款管理'
        ordering = ['term']

    @property
    def total(self):
        return self.principal + self.interest + self.penal_interest

    def __unicode__(self):
        return u'产品<%s>: 第 %s 期，总额 %s 元' % (self.product.short_name, self.term, self.total)


class P2PEquity(models.Model):
    user = models.ForeignKey(get_user_model(), related_name='equities')
    product = models.ForeignKey(P2PProduct, help_text=u'产品', related_name='equities')
    equity = models.BigIntegerField(verbose_name=u'用户所持份额', default=0)
    confirm = models.BooleanField(verbose_name=u'确认成功', default=False)

    paid_principal = models.DecimalField(verbose_name=u'已付本金', max_digits=20, decimal_places=2, default=Decimal(0))
    paid_interest = models.DecimalField(verbose_name=u'已付利息', max_digits=20, decimal_places=2, default=Decimal(0))
    penal_interest = models.DecimalField(verbose_name=u'已得罚息', max_digits=20, decimal_places=2, default=Decimal(0))
    term = models.IntegerField(verbose_name=u'已还期数', default=0)
    total_term = models.IntegerField(verbose_name=u'总期数', default=12)
    next_term = models.CharField(verbose_name=u'下期时间', max_length=100, default='', blank=True)
    next_amount = models.DecimalField(verbose_name=u'下期总数', max_digits=20, decimal_places=2, default=Decimal(0))
    total_interest = models.DecimalField(verbose_name=u'应付利息', max_digits=20, decimal_places=2, default=Decimal(0))

    class Meta:
        unique_together = (('user', 'product'),)
        verbose_name_plural = u'用户持仓'

    def __unicode__(self):
        return u'%s 持有 %s 数量:%s' % (self.user, self.product, self.equity)

    @property
    def related_orders(self):
        records = list()
        return records

    @property
    def ratio(self):
        return Decimal(self.equity) / Decimal(self.product.total_amount)


class AmortizationRecord(models.Model):
    catalog = models.CharField(verbose_name=u'流水类型', max_length=100)
    amortization = models.ForeignKey(ProductAmortization, related_name=u'to_users')
    order_id = models.IntegerField(verbose_name=u'关联订单编号', null=True)

    term = models.IntegerField(verbose_name=u'还款期数')
    principal = models.DecimalField(verbose_name=u'返还本金', max_digits=20, decimal_places=2)
    interest = models.DecimalField(verbose_name=u'返还利息', max_digits=20, decimal_places=2)
    penal_interest = models.DecimalField(verbose_name=u'额外罚息', max_digits=20, decimal_places=2)

    user = models.ForeignKey(get_user_model())
    created_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    description = models.CharField(verbose_name=u'摘要', max_length=1000)

    class Meta:
        verbose_name_plural = u'还款流水'

    @property
    def total(self):
        return self.principal + self.interest + self.penal_interest

    def __unicode__(self):
        return u'用户 %s 产品 %s 还款 %s' % (self.user, self.amortization.product, self.total)


class P2PRecord(models.Model):
    catalog = models.CharField(verbose_name=u'流水类型', max_length=100)
    order_id = models.IntegerField(verbose_name=u'关联订单编号', null=True)
    amount = models.DecimalField(verbose_name=u'发生数', max_digits=20, decimal_places=2)

    product = models.ForeignKey(P2PProduct, help_text=u'标的产品', null=True, on_delete=models.SET_NULL)
    product_balance_after = models.IntegerField(verbose_name=u'标的后余额', help_text=u'该笔流水发生后标的剩余量', null=True)

    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)

    create_time = models.DateTimeField(verbose_name=u'发生时间', auto_now_add=True)

    description = models.CharField(verbose_name=u'摘要', default='', max_length=1000)

    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'产品流水'

    def __unicode__(self):
        return u'流水号%s %s 发生金额%s' %(self.id, self.catalog, self.amount)

    def get_hash_list(self):
        return gen_hash_list(self.catalog, self.order_id, self.user.id, self.product.id, self.amount, self.create_time)


class EquityRecord(models.Model):
    catalog = models.CharField(verbose_name=u'流水类型', max_length=100)
    order_id = models.IntegerField(verbose_name=u'相关流水号', null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(P2PProduct, verbose_name=u'产品', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(verbose_name=u'发生数量', max_digits=20, decimal_places=2)
    description = models.CharField(verbose_name=u'摘要', max_length=1000, default=u'')

    create_time = models.DateTimeField(verbose_name=u'流水时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = u'持仓流水'

    def __unicode__(self):
        return u'%s %s %s %s' %(self.catalog, self.user, self.product, self.amount)
