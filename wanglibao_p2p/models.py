# encoding: utf-8
import collections
from decimal import Decimal
from django.db import models
from django.db.models import F
from django.utils import timezone
from jsonfield import JSONField
from wanglibao.models import ProductBase
from django.contrib.auth import get_user_model

user_model = get_user_model()


class WarrantCompany(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'名字')

    def __unicode__(self):
        return u'%s' % self.name


class P2PProductManager(models.Manager):
    def get_queryset(self):
        return super(P2PProductManager, self).get_queryset().filter(total_amount__exact=F('ordered_amount'),
                                                                    status__exact=u'正在招标')


class P2PProduct(ProductBase):
    name = models.CharField(max_length=256, verbose_name=u'名字')
    short_name = models.CharField(max_length=64, verbose_name=u'短名字')

    status = models.CharField(max_length=16, default=u'正在招标', verbose_name=u'产品装态(正在招标，已满标，还款中)')

    period = models.IntegerField(default=0, verbose_name=u'产品期限(月)')
    brief = models.TextField(blank=True, verbose_name=u'产品点评')
    expected_earning_rate = models.FloatField(default=0, verbose_name=u'预期收益(%)')
    closed = models.BooleanField(verbose_name=u'是否完结', default=False)

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


class TradeRecordType(models.Model):
    name = models.CharField(max_length=10, help_text=u'类型')
    description = models.CharField(max_length=200, help_text=u'类型说明')
    catalog_id = models.IntegerField(verbose_name=u'类型序号', unique=True, null=True)

    def __unicode__(self):
        return u'<流水类型: %s>' % self.name


class TradeRecord(models.Model):
    catalog = models.ForeignKey(TradeRecordType, help_text=u'流水类型')
    amount = models.DecimalField(verbose_name=u'发生数', max_digits=20, decimal_places=2)

    product = models.ForeignKey(P2PProduct, help_text=u'标的产品')
    product_balance_before = models.IntegerField(verbose_name=u'标的前余额', help_text=u'该笔流水发生前标的剩余量')
    product_balance_after = models.IntegerField(verbose_name=u'标的后余额', help_text=u'该笔流水发生后标的剩余量')

    user = models.ForeignKey(user_model)
    user_margin_before= models.DecimalField(verbose_name=u'用户前余额', help_text=u'该笔流水发生前用户余额', max_digits=20,
                                              decimal_places=2)
    user_margin_after= models.DecimalField(verbose_name=u'用户后余额', help_text=u'该笔流水发生后用户余额', max_digits=20,
                                             decimal_places=2)

    cancelable = models.BooleanField(verbose_name=u'可撤单', default=False)

    operation_ip = models.IPAddressField(verbose_name=u'流水ip', default='')
    operation_request_headers = models.TextField(verbose_name=u'流水请求信息', max_length=1000, default='',
                                                 help_text=u'存储流水产生时request headers信息')

    create_time = models.DateTimeField(verbose_name=u'发生时间', auto_now_add=True)

    checksum = models.CharField(verbose_name=u'签名', max_length=1000, default='')

    class Meta:
        ordering = ['-create_time']

    def __unicode__(self):
        return u'流水号%s %s 发生金额%s' %(self.id, self.catalog.name, self.amount)

    def get_hash_list(self):
        hash_list = list()
        hash_list.append(self.catalog.id)
        hash_list.append(self.amount)
        hash_list.append(self.product.id)
        hash_list.append(self.product_balance_before)
        hash_list.append(self.product_balance_after)
        hash_list.append(self.user.id)
        hash_list.append(self.create_time)
        return [str(item) for item in hash_list]


class UserMargin(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)
    margin = models.DecimalField(verbose_name=u'用户余额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    freeze = models.DecimalField(verbose_name=u'冻结金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    withdrawing = models.DecimalField(verbose_name=u'提款中金额', max_digits=20, decimal_places=2,
                                        default=Decimal('0.00'))

    def __unicode__(self):
        return '%s margin: %s, freeze: %s' % (self.user, self.margin, self.freeze)

    def has_margin(self, amount):
        amount = Decimal(amount)
        if amount <= self.margin:
            return True
        return False


class UserEquity(models.Model):
    user = models.ForeignKey(get_user_model(), related_name='equities')
    product = models.ForeignKey(P2PProduct, help_text=u'产品', related_name='equities')
    equity = models.BigIntegerField(verbose_name=u'用户所持份额', default=0)
    confirm = models.BooleanField(verbose_name=u'确认成功', default=False)

    class Meta:
        unique_together = (('user', 'product'),)

    def __unicode__(self):
        return u'%s 持有 %s 数量:%s' % (self.user, self.product, self.equity)

    #todo define a method can return all related trade record.
    @property
    def related_records(self):
        records = list()
        return records
