# encoding: utf-8
from decimal import Decimal

import redis
import simplejson
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User


# Create your models here.
from wanglibao import settings


class Margin(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    margin = models.DecimalField(verbose_name=u'用户余额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    freeze = models.DecimalField(verbose_name=u'冻结金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    withdrawing = models.DecimalField(verbose_name=u'提款中金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    invest = models.DecimalField(verbose_name=u'已投资金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    uninvested = models.DecimalField(verbose_name=u'充值未投资金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))
    uninvested_freeze = models.DecimalField(verbose_name=u'充值未投资冻结金额', max_digits=20, decimal_places=2, default=Decimal('0.00'))

    def __unicode__(self):
        return u'%s margin: %s, freeze: %s' % (self.user, self.margin, self.freeze)

    def has_margin(self, amount):
        amount = Decimal(amount)
        if amount <= self.margin:
            return True
        return False


class MarginRecord(models.Model):
    catalog = models.CharField(verbose_name=u'流水类型', max_length=100)
    order_id = models.IntegerField(verbose_name=u'相关订单编号', null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    create_time = models.DateTimeField(verbose_name=u'流水时间', auto_now_add=True)

    amount = models.DecimalField(verbose_name=u'发生金额', max_digits=20, decimal_places=2)
    margin_current = models.DecimalField(verbose_name=u'用户后余额', max_digits=20, decimal_places=2)
    description = models.CharField(verbose_name=u'摘要', max_length=1000, default=u'')

    def __unicode__(self):
        return u'%s , %s, 交易金额%s, 余额%s' % (self.catalog, self.user, self.amount, self.margin_current)

    class Meta:
        ordering = ['-create_time']


class PhpRefundRecord(models.Model):
    """
    针对月利宝产品到期回款流水记录, 有月利宝和债转两种回款
    """
    CATALOG = (
        ("0", "月利宝"),
        ("1", "债权转让"),
    )
    refund_id = models.IntegerField(verbose_name=u'相关订单编号', unique=True, null=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    catalog = models.CharField(db_index=True, verbose_name=u'购买类型',
                               choices=CATALOG, default='0', max_length=32)
    amount = models.DecimalField(verbose_name=u'发生金额', max_digits=20, decimal_places=2)
    margin_current = models.DecimalField(verbose_name=u'用户后余额', max_digits=20, decimal_places=2)
    description = models.CharField(verbose_name=u'摘要', max_length=1000, default=u'')

    create_at = models.DateTimeField(verbose_name=u'流水时间', auto_now_add=True)

    def __unicode__(self):
        return u'%s , %s, 交易金额%s, 余额%s' % (self.catalog, self.user, self.amount, self.margin_current)

    class Meta:
        ordering = ['-create_at']


class MonthProduct(models.Model):
    """
    月利宝model, 记录主要字段.
    """
    RED_PACKET_TYPE = (
        ("-1", u"加息不存在"),
        ("0", u"加息券加息"),
        ("1", u"红包加息"),
    )
    TRADE_STATUS = (
        ('New', u'未处理'),
        ('PAID', u'支付成功'),
        ('FAILED', u'支付失败'),
    )

    user = models.ForeignKey(User, related_name='month_product_buyer', verbose_name=u'买家')
    product_id = models.CharField(verbose_name=u'月利宝产品ID', max_length=100)
    trade_id = models.CharField(verbose_name=u'交易ID', max_length=100)
    token = models.CharField(db_index=True, verbose_name=u'订单号token', unique=True, max_length=64)
    amount = models.DecimalField(verbose_name=u'交易金额', max_digits=12, decimal_places=2)
    amount_source = models.DecimalField(verbose_name=u'交易金额', max_digits=12, decimal_places=2)
    red_packet = models.DecimalField(verbose_name=u'红包金额', max_digits=10, decimal_places=2)
    red_packet_type = models.CharField(db_index=True, verbose_name=u'红包类型',
                                       choices=RED_PACKET_TYPE, default='-1', max_length=32)

    cancel_status = models.BooleanField(default=False, verbose_name=u'是否已取消')   # 流标, 用户冻结金额恢复状态
    trade_status = models.CharField(choices=TRADE_STATUS, default='NEW', max_length=8, verbose_name=u'交易状态')

    created_at = models.DateTimeField(verbose_name=u'月利宝生效时间', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class AssignmentOfClaims(models.Model):
    """
    债权转让model, 记录主要字段.
    buy_price = buy_price_source + 手续费
    sell_price = sell_price_source + premium_fee + fee
    """
    TRADE_STATUS = (
        ('New', u'未处理'),
        ('PAID', u'支付成功'),
        ('FAILED', u'支付失败'),
    )

    product_id = models.CharField(verbose_name=u'债权产品ID', max_length=100)
    buyer = models.ForeignKey(User, related_name='assignment_buyer', verbose_name=u'买家')
    seller = models.ForeignKey(User, related_name='assignment_seller', verbose_name=u'卖家')
    buyer_order_id = models.CharField(verbose_name=u'买方交易ID', max_length=32)
    seller_order_id = models.CharField(verbose_name=u'卖方交易ID', max_length=32)
    buyer_token = models.CharField(verbose_name=u'买方订单号', max_length=64)
    seller_token = models.CharField(verbose_name=u'卖方订单号', max_length=64)
    fee = models.DecimalField(verbose_name=u'卖家手续费(6/1000)', max_digits=12, decimal_places=2)
    # ( 售方 ) 被扣溢价费 , 价值 1000 卖 1200, 其中超过原金额的 200 元按 25% 收取费用 .
    premium_fee = models.DecimalField(verbose_name=u'被扣溢价费', max_digits=12, decimal_places=2)
    # tradingFee ( 买方 ) 被扣平台交易费 , 单笔债转产品购买费用 .
    trading_fee = models.DecimalField(verbose_name=u'债转产品购买费用', max_digits=12, decimal_places=2)
    buy_price = models.DecimalField(verbose_name=u'( 买方 ) 实付金额', max_digits=12, decimal_places=2)
    sell_price = models.DecimalField(verbose_name=u'( 售方 ) 实收金额', max_digits=12, decimal_places=2)
    buy_price_source = models.DecimalField(verbose_name=u'( 买方 )原始交易价格', max_digits=12, decimal_places=2)
    sell_price_source = models.DecimalField(verbose_name=u'( 售方 )原始交易价格', max_digits=12, decimal_places=2)

    # 只有在买卖双方的钱处理完毕之后才把状态置为True
    status = models.BooleanField(default=False, verbose_name=u'是否标记')
    trade_status = models.CharField(choices=TRADE_STATUS, default='NEW', max_length=8, verbose_name=u'交易状态')
    created_at = models.DateTimeField(verbose_name=u'债转生效时间', auto_now_add=True)

    def get_status(self):
        return u'成功' if self.status else u'失败'

    class Meta:
        ordering = ['-created_at']


def create_user_margin(sender, **kwargs):
    """
    create user margin after user object created.
    :param sender:
    :param kwargs:
    :return:
    """
    if kwargs['created']:
        user = kwargs['instance']
        margin = Margin(user=user)
        margin.save()


def save_margin_to_redis(sender, **kwargs):
    """
    when margin saved, update the user info in redis.
    """
    margin = kwargs["instance"]
    user = margin.user
    host = settings.PHP_REDIS_HOST
    port = settings.PHP_REDIS_PORT
    db = settings.PHP_REDIS_DB
    password = settings.PHP_REDIS_PASSWORD

    redis_pool = redis.ConnectionPool(host=host, port=port, db=db, password=password)
    redis_obj = redis.Redis(connection_pool=redis_pool)

    redis_keys = redis_obj.keys(pattern='python_{}_*'.format(user.pk))

    try:
        from wanglibao_p2p.models import P2PEquity

        data = simplejson.loads(redis_obj.get(redis_keys[0]))
        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
                    u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
                ]).select_related('product')
        unpayed_principle = 0

        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal  # 待收本金

        # 增加从PHP项目来的月利宝待收本金
        from wanglibao_margin.php_utils import get_php_redis_principle
        php_principle = get_php_redis_principle(user.pk)
        unpayed_principle += php_principle

        total_amount = unpayed_principle + margin.margin + margin.withdrawing + margin.freeze

        data.update(
             total_amount=total_amount,
             avaliable_amount=margin.margin,
             unpayed_principle=unpayed_principle,
             margin_freeze=margin.freeze,
             margin_withdrawing=margin.withdrawing,
        )

        for redis_key in redis_keys:
            redis_obj.set(redis_key, simplejson.dumps(data))

    except Exception, e:
        print e
        for key in redis_keys:
            redis_obj.delete(key)


post_save.connect(create_user_margin, sender=User, dispatch_uid='users-margin-creation-signal')
post_save.connect(save_margin_to_redis, sender=Margin, dispatch_uid="users-margin-save_to_redis-signal")
