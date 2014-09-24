# encoding: utf-8
import collections
import logging
from decimal import Decimal
from concurrency.fields import IntegerVersionField
from django.db import models
from django.db.models import F, Sum, SET_NULL
from django.db.models.signals import post_save
from django.utils import timezone
from django.contrib.auth import get_user_model
import reversion
from wanglibao.fields import JSONFieldUtf8
from wanglibao.models import ProductBase
from utility import gen_hash_list
from wanglibao_p2p.amortization_plan import get_amortization_plan

logger = logging.getLogger(__name__)


class WarrantCompany(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'名字')

    class Meta:
        verbose_name = u'担保公司'
        verbose_name_plural = u'担保公司'

    def __unicode__(self):
        return u'%s' % self.name


class ContractTemplate(models.Model):
    name = models.CharField(u'名字', max_length=32)
    content = models.TextField(u'模板内容', default='')

    class Meta:
        verbose_name_plural = u'借款合同'

    def __unicode__(self):
        return self.name


class P2PProduct(ProductBase):
    STATUS_CHOICES = (
        (u'录标', u'录标'),
        (u'录标完成', u'录标完成'),
        (u'待审核', u'待审核'),
        (u'正在招标', u'正在招标'),
        (u'满标待打款', u'满标待打款'),
        (u'满标已打款', u'满标已打款'),
        (u'满标待审核', u'满标待审核'),
        (u'满标已审核', u'满标已审核'),
        (u'还款中', u'还款中'),
        (u'流标', u'流标'),
        (u'已完成', u'已完成')
    )

    CATEGORY_CHOICES = (
        (u'普通', u'普通'),
        (u'证大速贷', u'证大速贷')
    )

    PAY_METHOD_CHOICES = (
        (u'等额本息', u'等额本息'),
        (u'先息后本', u'先息后本'),
        (u'按月付息', u'按月付息到期还本'),
        (u'到期还本付息', u'到期还本付息'),
        (u'按季度付息', u'按季度付息'),
    )
    BANK_METHOD_CHOICES = (
        (u'工商银行',u'工商银行'),
        (u'农业银行',u'农业银行'),
        (u'招商银行',u'招商银行'),
        (u'建设银行',u'建设银行'),
        (u'北京银行',u'北京银行'),
        (u'北京农村商业银行', u'北京农村商业银行'),
        (u'中国银行', u'中国银行'),
        (u'交通银行', u'交通银行'),
        (u'民生银行', u'民生银行'),
        (u'上海银行', u'上海银行'),
        (u'渤海银行', u'渤海银行'),
        (u'光大银行', u'光大银行'),
        (u'兴业银行', u'兴业银行'),
        (u'中信银行', u'中信银行'),
        (u'浙商银行', u'浙商银行'),
        (u'广发银行', u'广发银行'),
        (u'东亚银行', u'东亚银行'),
        (u'华夏银行', u'华夏银行'),
        (u'杭州银行', u'杭州银行'),
        (u'南京银行', u'南京银行'),
        (u'平安银行', u'平安银行'),
        (u'邮政储蓄银行', u'邮政储蓄银行'),
        (u'深圳发展银行', u'深圳发展银行'),
        (u'上海浦东发展银行',u'上海浦东发展银行'),
        (u'上海农村商业银行',u'上海农村商业银行'),
        (u'汇付天下', u'汇付天下'),
    )

    version = IntegerVersionField()
    category = models.CharField(max_length=16, default=u'普通',
                              choices=CATEGORY_CHOICES,
                              verbose_name=u'产品类别*')

    hide = models.BooleanField(u'隐藏', default=False)

    name = models.CharField(max_length=256, verbose_name=u'名字*', blank=False)
    short_name = models.CharField(verbose_name=u'短名字*', max_length=64, blank=False)
    serial_number = models.CharField(verbose_name=u'产品编号*', max_length=100, unique=True, blank=False, null=True)
    contract_serial_number = models.CharField(verbose_name=u'合同编号*', max_length=100, blank=False, null=True)

    status = models.CharField(max_length=16, default=u'录标',
                              choices=STATUS_CHOICES,
                              verbose_name=u'产品状态*')
    priority = models.IntegerField(verbose_name=u'优先级*', help_text=u'越大越优先', blank=False)
    period = models.IntegerField(default=0, verbose_name=u'产品期限(月)*', blank=False)
    brief = models.TextField(blank=True, verbose_name=u'产品点评')
    expected_earning_rate = models.FloatField(default=0, verbose_name=u'预期收益(%)*', blank=False)
    excess_earning_rate = models.FloatField(default=0, verbose_name=u'超额收益(%)*')
    excess_earning_description = models.CharField(u'超额收益描述', max_length=100, blank=True, null=True)

    pay_method = models.CharField(verbose_name=u'支付方式*', max_length=32, blank=False, default=u'等额本息', choices=PAY_METHOD_CHOICES)
    amortization_count = models.IntegerField(u'还款期数', default=0)
    repaying_source = models.TextField(verbose_name=u'还款资金来源(合同用)', blank=True)

    # Bao li related
    baoli_original_contract_number = models.CharField(u'(保理)原合同编号', max_length=64, blank=True)
    baoli_original_contract_name = models.CharField(u'(保理)原合同名字', max_length=128, blank=True)
    baoli_trade_relation = models.CharField(u'(保理)交易关系', max_length=128, blank=True)

    # pay info for the borrower
    borrower_name = models.CharField(verbose_name=u'借债人姓名*', max_length=32, blank=False)
    borrower_phone = models.CharField(verbose_name=u'借债人手机号*', max_length=32, blank=False)
    borrower_address = models.CharField(verbose_name=u'借债人地址*', max_length=128, blank=False)
    borrower_id_number = models.CharField(verbose_name=u'借债人身份证号*', max_length=32, blank=False)
    borrower_bankcard = models.CharField(verbose_name=u'借债人银行卡号*', max_length=64, blank=False)
    borrower_bankcard_bank_name = models.CharField(verbose_name=u'开户行*', max_length=64, blank=False)
    borrower_bankcard_bank_code = models.CharField(verbose_name=u'借债人银行(汇付表格专用)*',choices=BANK_METHOD_CHOICES, max_length=64, blank=False)
    borrower_bankcard_bank_province = models.CharField(u'借债人银行省份', max_length=64, blank=True)
    borrower_bankcard_bank_city = models.CharField(u'借债人地区', max_length=64, blank=True)
    borrower_bankcard_bank_branch = models.CharField(u'借债人支行', max_length=64, blank=True)

    total_amount = models.BigIntegerField(default=1, verbose_name=u'借款总额*', blank=False)
    ordered_amount = models.BigIntegerField(default=0, verbose_name=u'已募集金额*')

    # _available_amout = models.BigIntegerField(default=0, verbose_name=u'可投资金额')

    extra_data = JSONFieldUtf8(blank=True, load_kwargs={'object_pairs_hook': collections.OrderedDict})

    publish_time = models.DateTimeField(default=timezone.now, verbose_name=u'发布时间*', blank=False)
    end_time = models.DateTimeField(default=timezone.now, verbose_name=u'终止时间*', blank=False)
    soldout_time = models.DateTimeField(u'售完时间', null=True, blank=True)

    limit_per_user = models.FloatField(verbose_name=u'单用户购买限额(0-1的系数)*', default=1)

    warrant_company = models.ForeignKey(WarrantCompany,blank=False)
    usage = models.TextField(blank=False, verbose_name=u'借款用途(合同用)*')
    short_usage = models.TextField(blank=False, verbose_name=u'借款用途*')

    contract_template = models.ForeignKey(ContractTemplate, on_delete=SET_NULL, null=True ,blank=False)

    class Meta:
        verbose_name_plural = u'P2P产品'

    def __unicode__(self):
        return u'<%s>' % self.name

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

    @property
    def available_amout(self):
        return self.total_amount - self.ordered_amount

    def has_amount(self, amount):
        if amount <= self.remain:
            return True
        return False

    def audit_link(self):
        if self.status == u'满标待审核':
            return u'<a href="/p2p/audit/%d/" class="link">审核</a>' % self.id
        else:
            return u'-'

    audit_link.short_description = u'审核'
    audit_link.allow_tags = True

    def preview_link(self):
        return u'<a href="/p2p/detail/%s" target="_blank">预览</a>' % str(self.id)
    preview_link.short_description = u'预览'
    preview_link.allow_tags = True

    display_status_mapping = {
        u'录标': u'录标',
        u'录标完成': u'录标完成',
        u'待审核': u'待审核',
        u'正在招标': u'抢购中',
        u'满标待打款': u'满标审核',
        u'满标已打款': u'满标审核',
        u'满标待审核': u'满标审核',
        u'满标已审核': u'满标审核',
        u'还款中': u'还款中',
        u'流标': u'流标',
        u'已完成': u'已完成',
    }

    @property
    def display_status(self):
        return self.display_status_mapping[self.status]


    display_payback_mapping = {
        u'等额本息': u'等额本息',
        u'先息后本': u'先息后本',
        u'按月付息': u'按月付息到期还本',
        u'到期还本付息': u'一次性还本付息',
        u'按季度付息': u'按季度付息',
    }

    @property
    def display_payback_method(self):
        if self.pay_method in self.display_payback_mapping:
            return self.display_payback_mapping[self.pay_method]
        return self.pay_method


reversion.register(P2PProduct)


class Warrant(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'名字')
    warranted_at = models.DateTimeField(default=timezone.now, verbose_name=u'认证时间')
    created_at = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')

    product = models.ForeignKey(P2PProduct)

    class Meta:
        verbose_name_plural = u'担保细节'

    def __unicode__(self):
        return u'%s %s %s' % (str(self.product_id), self.name, str(self.warranted_at))


class Attachment(models.Model):
    product = models.ForeignKey(P2PProduct)
    name = models.CharField(u'名字', max_length=128)
    description = models.TextField(u'描述')
    type = models.CharField(u'类型', max_length=32)
    file = models.FileField(upload_to='attachment')
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.name


class AmortizationReadyManager(models.Manager):
    def get_queryset(self):
        return super(AmortizationReadyManager, self).get_queryset().filter(term_date__lte=timezone.now(),
                                                                           ready_for_settle=True,
                                                                           settled=False)


class ProductAmortization(models.Model):

    version = IntegerVersionField()

    product = models.ForeignKey(P2PProduct, related_name='amortizations')

    term = models.IntegerField(u'还款期数')
    term_date = models.DateTimeField(u'还款时间', null=True, blank=True)
    principal = models.DecimalField(u'返还本金', max_digits=20, decimal_places=2)
    interest = models.DecimalField(u'返还利息', max_digits=20, decimal_places=2)
    penal_interest = models.DecimalField(u'额外罚息', max_digits=20, decimal_places=2, default=Decimal('0'))

    settled = models.BooleanField(u'已结算给客户', default=False, editable=False)
    settlement_time = models.DateTimeField(u'结算时间', auto_now=True)

    ready_for_settle = models.BooleanField(u'是否可以开始结算', default=False)

    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    description = models.CharField(u'摘要', max_length=500, blank=True)

    objects = models.Manager()
    is_ready = AmortizationReadyManager()

    class Meta:
        verbose_name_plural = u'产品还款计划'
        ordering = ['term']

    @property
    def total(self):
        return self.principal + self.interest + self.penal_interest

    def __unicode__(self):
        return u'产品%s: 第 %s 期' % (str(self.product_id), self.term)


class UserAmortization(models.Model):
    version = IntegerVersionField()

    product_amortization = models.ForeignKey(ProductAmortization, related_name='subs')
    user = models.ForeignKey(get_user_model())
    term = models.IntegerField(u'还款期数')
    term_date = models.DateTimeField(u'还款时间')
    principal = models.DecimalField(u'本金', max_digits=20, decimal_places=2)
    interest = models.DecimalField(u'利息', max_digits=20, decimal_places=2)
    penal_interest = models.DecimalField(u'罚息', max_digits=20, decimal_places=2, default=Decimal('0.00'))

    settled = models.BooleanField(u'已结算', default=False)
    settlement_time = models.DateTimeField(u'结算时间', auto_now=True)

    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    description = models.CharField(u'摘要', max_length=500, blank=True)

    class Meta:
        verbose_name_plural = u'用户还款计划'
        ordering = ['user', 'term']

    def __unicode__(self):
        return u'分期%s 用户%s 本金%s 利息%s' % (self.product_amortization, self.user, self.principal, self.interest)


class P2PEquity(models.Model):
    version = IntegerVersionField()

    user = models.ForeignKey(get_user_model(), related_name='equities')
    product = models.ForeignKey(P2PProduct, help_text=u'产品', related_name='equities')
    equity = models.BigIntegerField(u'用户所持份额', default=0)
    confirm = models.BooleanField(u'确认成功', default=False)
    confirm_at = models.DateTimeField(u'份额确认时间', null=True, blank=True)
    contract = models.FileField(u'合同文件', null=True, blank=True, upload_to='contracts')
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True, null=True)

    class Meta:
        unique_together = (('user', 'product'),)
        verbose_name_plural = u'用户持仓'
        ordering = ('-created_at',)

    @property
    def related_orders(self):
        records = list()
        return records

    @property
    def ratio(self):
        return Decimal(self.equity) / Decimal(self.product.total_amount)

    @property
    def term(self):
        amos = self.__get_amortizations(settled_only=True)
        return len(amos)

    @property
    def total_term(self):
        return self.product.amortization_count

    @property
    def total_interest(self):
        if not self.confirm:
            return Decimal('0')
        amortizations = self.__get_amortizations()
        if not amortizations:
            return Decimal('0')
        interest = amortizations.aggregate(Sum('interest'))['interest__sum']
        return interest

    @property
    def paid_interest(self):
        if not self.confirm:
            return Decimal('0')
        paid_amos = self.__get_amortizations(settled_only=True)
        if not paid_amos:
            return Decimal('0')
        paid_interest = paid_amos.aggregate(Sum('interest'))['interest__sum']
        return paid_interest

    @property
    def unpaid_interest(self):
        return self.total_interest - self.paid_interest

    @property
    def penal_interest(self):
        if not self.confirm:
            return Decimal('0')
        paid_amos = self.__get_amortizations(settled_only=True)
        if not paid_amos:
            return Decimal('0')
        penal_interest = paid_amos.aggregate(Sum('penal_interest'))['penal_interest__sum']
        return penal_interest

    @property
    def paid_principal(self):
        if not self.confirm:
            return Decimal('0')
        paid_amos = self.__get_amortizations(settled_only=True)
        if not paid_amos:
            return Decimal('0')
        paid_principal = paid_amos.aggregate(Sum('principal'))['principal__sum']
        return paid_principal

    @property
    def unpaid_principal(self):
        return self.equity - self.paid_principal

    @property
    def amortizations(self):
        return self.__get_amortizations()

    def __get_amortizations(self, settled_only=False):
        if settled_only:
            amortizations = UserAmortization.objects.filter(user=self.user, product_amortization__product=self.product,
                                                            settled=True)
        else:
            amortizations = UserAmortization.objects.filter(user=self.user, product_amortization__product=self.product)
        return amortizations


class AmortizationRecord(models.Model):
    catalog = models.CharField(u'流水类型', max_length=100)
    amortization = models.ForeignKey(ProductAmortization, related_name=u'to_users')
    order_id = models.IntegerField(u'关联订单编号', null=True)

    term = models.IntegerField(u'还款期数')
    principal = models.DecimalField(u'返还本金', max_digits=20, decimal_places=2)
    interest = models.DecimalField(u'返还利息', max_digits=20, decimal_places=2)
    penal_interest = models.DecimalField(u'额外罚息', max_digits=20, decimal_places=2)

    user = models.ForeignKey(get_user_model(), null=True)
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    description = models.CharField(u'摘要', max_length=1000)

    class Meta:
        verbose_name_plural = u'还款流水'

    @property
    def total(self):
        return self.principal + self.interest + self.penal_interest

    def __unicode__(self):
        return u'用户 %s 产品 %s 还款 %s' % (self.user, self.amortization.product, self.total)


class P2PRecord(models.Model):
    catalog = models.CharField(u'流水类型', max_length=100, db_index=True)
    order_id = models.IntegerField(u'关联订单编号', null=True)
    amount = models.DecimalField(u'发生数', max_digits=20, decimal_places=2)

    product = models.ForeignKey(P2PProduct, help_text=u'标的产品', null=True, on_delete=models.SET_NULL)
    product_balance_after = models.IntegerField(u'标的后余额', help_text=u'该笔流水发生后标的剩余量', null=True)

    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)

    create_time = models.DateTimeField(u'发生时间', auto_now_add=True)

    description = models.CharField(u'摘要', default='', max_length=1000)

    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = u'产品流水'

    def __unicode__(self):
        return u'流水号%s %s 发生金额%s' % (self.id, self.catalog, self.amount)

    def get_hash_list(self):
        return gen_hash_list(self.catalog, self.order_id, self.user.id, self.product.id, self.amount, self.create_time)


class EquityRecord(models.Model):
    catalog = models.CharField(u'流水类型', max_length=100)
    order_id = models.IntegerField(u'相关流水号', null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(P2PProduct, verbose_name=u'产品', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(u'发生数量', max_digits=20, decimal_places=2)
    description = models.CharField(u'摘要', max_length=1000, default=u'')

    create_time = models.DateTimeField(u'流水时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = u'持仓流水'

    def __unicode__(self):
        return u'%s %s %s %s' % (self.catalog, self.user, self.product, self.amount)


def generate_amortization_plan(sender, instance, **kwargs):
    if instance.status == u'录标完成':
        logger.info(u'The product status is 录标完成, start to generate amortization plan')

        terms = get_amortization_plan(instance.pay_method).generate(instance.total_amount, instance.expected_earning_rate / 100, None, instance.period)

        for index, term in enumerate(terms['terms']):
            amortization = ProductAmortization()
            amortization.description = u'第%d期' % (index + 1)
            amortization.principal = term[1]
            amortization.interest = term[2]
            amortization.term = index + 1
            instance.amortizations.add(amortization)
            amortization.save()

        instance.amortization_count = len(terms['terms'])

        instance.status = u'待审核'
        instance.save()


def process_after_money_paided(product):
    if product.status == u'满标已打款':
        from celery.execute import send_task
        send_task("wanglibao_p2p.tasks.process_paid_product", kwargs={
            'product_id': product.id
        })


def post_save_process(sender, instance, **kwargs):
    generate_amortization_plan(sender, instance, **kwargs)
    process_after_money_paided(instance)

post_save.connect(post_save_process, sender=P2PProduct, dispatch_uid="generate_amortization_plan")