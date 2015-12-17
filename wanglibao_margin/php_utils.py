# -*- coding: utf-8 -*-
import decimal
from decimal import Decimal

import datetime
import redis
import requests
import simplejson
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from user_agents import parse

from marketing.models import IntroducedBy
from wanglibao import settings
from wanglibao_margin.exceptions import MarginLack
from wanglibao_margin.marginkeeper import MarginKeeper, check_amount
from wanglibao_margin.models import Margin, MarginRecord, MonthProduct, PhpRefundRecord
from wanglibao_p2p.models import P2PEquity
from wanglibao_redpack.models import PhpIncome
# from weixin.util import getAccountInfo


def set_cookie(response, key, value, hours_expire=1, domain=settings.SESSION_COOKIE_DOMAIN):
    """
    set cookie for PHP to judge the login statement.
    :param response:
    :param key:
    :param value:
    :param hours_expire:
    :param domain:
    :return:
    """
    expires = datetime.datetime.now() + datetime.timedelta(hours=hours_expire)
    response.set_cookie(key, value, expires=expires, domain=domain)


class PhpRedisBackend(object):

    def __init__(self, host=settings.PHP_REDIS_HOST, port=settings.PHP_REDIS_PORT, db=settings.PHP_REDIS_DB):
        try:
            self.password = settings.PHP_REDIS_PASSWORD
            self.pool = redis.ConnectionPool(host=host, port=port, db=db, password=self.password)
            self.redis = redis.Redis(connection_pool=self.pool)
            self.redis.set("php_test", "php_test")
        except:
            self.pool = None
            self.redis = None

    def _is_available(self):
        try:
            self.redis.ping()
        except:
            return False
        return True

    def _exists(self, name):
        if self.redis:
            return self.redis.exists(name)
        return False

    def _set(self, key, value):
        if self.redis:
            self.redis.set(key, value)

    def _get(self, key):
        if self.redis:
            return self.redis.get(key)
        return None

    def _delete(self, key):
        if self.redis:
            self.redis.delete(key)

    def _lpush(self, key, value):
        if self.redis:
            self.redis.lpush(key, value)

    def _rpush(self, key, value):
        if self.redis:
            self.redis.rpush(key, value)

    def _lrange(self, key, start, end):
        if self.redis:
            return self.redis.lrange(key, start, end)

    def _lrem(self, key, value, count=0):
        if self.redis:
            self.redis.lrem(key, value, count)


class PhpMarginKeeper(MarginKeeper):

    def margin_process(self, user, status, amount, description=u'', catalog=u'', savepoint=True):
        """
        # 这是直接对用户余额进行加减. 适用于债权转让的处理.
        # 同时需要对用户的充值未投资金额进行处理.
        :param user:    用户
        :param status:  加钱还是扣钱 0 是加钱, 其他扣钱
        :param amount:  金额
        :param description: 描述
        :param catalog: 分类
        :param savepoint:   一个事务操作.
        :return:
        """
        with transaction.atomic(savepoint=savepoint):
            amount = Decimal(amount)
            check_amount(amount)
            margin = Margin.objects.get(user=user)
            if status == 0:
                margin.margin += amount
            else:
                margin.margin -= amount
                margin_uninvested = margin.uninvested  # 初始未投资余额
                uninvested = margin.uninvested - amount  # 未投资金额 - 投资金额 = 未投资余额计算结果
                margin.uninvested = uninvested if uninvested >= 0 else Decimal('0.00')  # 未投资余额计算结果<0时,结果置0
                margin.uninvested_freeze += amount if uninvested >= 0 else margin_uninvested  # 未投资余额计算结果<0时,未投资冻结金额等于+初始未投资余额
            margin.save()
            record = self.tracer(catalog, amount, margin.margin, description)
            return record

    def yue_cancel(self, user, amount, description=u'月利宝购买失败', catalog=u'月利宝购买失败回滚', savepoint=True):
        """
        # 月利宝购买失败回滚.
        :param user:  请求用户
        :param amount:  金额
        :param description: 描述
        :param catalog: 分类
        :param savepoint:   一个事务操作.
        :return:
        """
        with transaction.atomic(savepoint=savepoint):
            amount = Decimal(amount)
            check_amount(amount)
            margin = Margin.objects.select_for_update().filter(user=user).first()
            if amount > margin.freeze:
                raise MarginLack(u'202')

            margin.margin += amount
            margin.freeze -= amount

            margin.save()
            record = self.tracer(catalog, amount, margin.margin, description)
            return record

    def deposit(self, amount, description=u'', savepoint=True, catalog=u"现金存入"):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            margin.margin += amount
            if catalog == u'现金存入':
                margin.uninvested += amount  # 充值未投资金融
            margin.save()
            catalog = catalog
            record = self.tracer(catalog, amount, margin.margin, description)
            return record

    def tracer(self, catalog, amount, margin_current, description=u'', order_id=None):
        if not order_id:
            order_id = self.order_id
        trace = MarginRecord(catalog=catalog, amount=amount, margin_current=margin_current, description=description,
                             order_id=order_id, user=self.user)
        trace.save()
        return trace

    def php_amortize(self, refund_id, user, catalog, amount, description, savepoint=True):
        """
        月利宝到期回款, 用户只加总额, 操作后写流水日志. 详细写在description里.
        :param refund_id:       唯一回款ID, 不可重复.
        :param user:            对应用户
        :param catalog:         0: 月利宝, 1: 债权转让
        :param amount:          回款总金额
        :param description:     回款所有细节
        :param savepoint:       原子操作标记
        :return:
        """
        check_amount(amount)
        amount = Decimal(amount)

        with transaction.atomic(savepoint=savepoint):
            if not PhpRefundRecord.objects.filter(refund_id=refund_id).first():
                margin = Margin.objects.select_for_update().filter(user=self.user).first()
                margin.margin += amount
                margin.save()
                try:
                    PhpRefundRecord.objects.get_or_create(
                        refund_id=refund_id, user=user, catalog=catalog,
                        amount=amount, margin_current=margin.margin, description=description)
                    return 1
                except Exception, e:
                    print e

    def php_amortize_detail(self, category, principal, interest, penal_interest, coupon_interest, platform_interest,
                            refund_id, savepoint=True):
        """
        针对php 的还款详细写记录
        :param category                 类型, 0 月利宝; 1 债转
        :param principal:           本金
        :param interest:            利息
        :param penal_interest:      罚息
        :param coupon_interest:     红包加息
        :param platform_interest:   平台加息
        :param refund_id:           订单号(唯一值)
        :param savepoint:
        :return:
        """
        check_amount(principal)
        check_amount(interest)
        check_amount(penal_interest)
        principal = Decimal(principal)
        interest = Decimal(interest)
        penal_interest = Decimal(penal_interest)
        coupon_interest = Decimal(coupon_interest)
        platform_interest = Decimal(platform_interest)

        with transaction.atomic(savepoint=savepoint):

            margin = Margin.objects.select_for_update().filter(user=self.user).first()

            if category == '0':
                margin.margin += principal
                self.tracer(u'月利宝本金入账', principal, margin.margin, u'月利宝本金入账', refund_id)
                margin.margin += interest
                self.tracer(u'月利宝利息入账', interest, margin.margin, u'月利宝利息入账', refund_id)
                if penal_interest > 0:
                    margin.margin += penal_interest
                    self.tracer(u'月利宝罚息入账', penal_interest, margin.margin, u'月利宝罚息入账', refund_id)
                if platform_interest > 0:
                    margin.margin += platform_interest
                    self.tracer(u'月利宝平台加息入账', platform_interest, margin.margin, u'月利宝平台加息入账', refund_id)
                if coupon_interest > 0:
                    margin.margin += coupon_interest
                    description = u"月利宝加息存入{}元".format(coupon_interest)
                    # self.hike_deposit(coupon_interest, u"加息存入{}元".format(coupon_interest), order_id, savepoint=False)
                    self.tracer(u"月利宝加息存入", coupon_interest, margin.margin, description, refund_id)

            if category == '1':
                margin.margin += principal
                self.tracer(u'债转本金入账', principal, margin.margin, u'债转本金入账', refund_id)
                margin.margin += interest
                self.tracer(u'债转利息入账', interest, margin.margin, u'债转利息入账', refund_id)
                if penal_interest > 0:
                    margin.margin += penal_interest
                    self.tracer(u'债转罚息入账', penal_interest, margin.margin, u'债转罚息入账', refund_id)
                if platform_interest > 0:
                    margin.margin += platform_interest
                    self.tracer(u'债转平台加息入账', penal_interest, margin.margin, u'债转平台加息入账', refund_id)
                if coupon_interest > 0:
                    margin.margin += coupon_interest
                    description = u"债转加息存入{}元".format(coupon_interest)
                    # self.hike_deposit(coupon_interest, u"加息存入{}元".format(coupon_interest), order_id, savepoint=False)
                    self.tracer(u"债转加息存入", coupon_interest, margin.margin, description, refund_id)
            margin.save()


def get_user_info(request, session_id):
    """
    get user's base info to php server.
    :param request:
    :param session_id:
    :return:
    from_channel, 登录渠道 . 如 :PC
    isAdmin
    """
    user_info = dict()

    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)

    print 'ua_string = ', ua_string
    print 'user agent = ', user_agent

    if session_id == request.session.session_key:
        user = request.user

        if not user.id:
            user_info.update(status=0,
                             message=u'session error.')
            return user_info

        margin_info = get_margin_info(user.id)

        user_info.update(user_id=user.pk,
                         username=user.wanglibaouserprofile.phone,
                         realname=user.wanglibaouserprofile.name,
                         is_disable=user.wanglibaouserprofile.frozen,
                         is_realname=1 if user.wanglibaouserprofile.id_is_valid else 0,
                         total_amount=margin_info.get('total_amount'),
                         avaliable_amount=margin_info.get('margin'),
                         unpayed_principle=margin_info.get('unpayed_principle'),
                         margin_freeze=margin_info.get('margin_freeze'),
                         margin_withdrawing=margin_info.get('margin_withdrawing'),
                         from_channel=ua_string,
                         is_admin=user.is_superuser,
                         id_number=user.wanglibaouserprofile.id_number)

        # save to redis if not exist else update.
        redis_obj = PhpRedisBackend()
        redis_obj.redis.set('python_{}_{}'.format(user.id, session_id), simplejson.dumps(user_info))
        redis_obj.redis.expire('python_{}_{}'.format(user.id, session_id), 1440)
    else:
        user_info.update(status=0,
                         message=u'session error.')

    return user_info


def get_margin_info(user_id):
    """
    :param user_id:
    :return: 用户可用余额
    0.00 总资产(元) = 0.00 可用余额 + 0.00 待收本金 + 0.00 投资冻结 + 0.00 提现冻结
    """

    try:
        user = User.objects.get(pk=user_id)
        # 不验证登录用户是不是请求用户
        # if user and request.user == user:
        if user:
            p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
                        u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
                    ]).select_related('product')
            unpaid_principle = 0
            for equity in p2p_equities:
                if equity.confirm:
                    unpaid_principle += equity.unpaid_principal  # 待收本金

            # 增加从PHP项目来的月利宝待收本金
            php_principle = get_php_redis_principle(user.pk)
            unpaid_principle += php_principle

            margin = user.margin.margin
            margin_freeze = user.margin.freeze
            margin_withdrawing = user.margin.withdrawing
            total_amount = margin + margin_freeze + margin_withdrawing + unpaid_principle

            return {'state': True, 'margin': margin, 'total_amount': total_amount, 'unpayed_principle': unpaid_principle,
                    'margin_freeze': margin_freeze, 'margin_withdrawing': margin_withdrawing}
    except Exception, e:
        print e

    return {'state': False, 'info': 'user authenticated error!'}


def php_commission_exist(product_id):
    record = PhpIncome.objects.filter(product_id=product_id).first()
    return record


def php_commission(user, product_id, start, end):
    """
    月利宝的表存的是php那边的流水.直接从这获取
    :param user:
    :param product_id:
    :param equity:
    :param start:
    :param end:
    :return:
    """
    _amount = MonthProduct.objects.filter(user=user, product_id=product_id, created_at__gt=start,
                                          created_at__lt=end).aggregate(Sum('amount'))
    if _amount['amount__sum']:
        commission = decimal.Decimal(_amount['amount__sum']) * decimal.Decimal("0.003")
        commission = commission.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
        first_intro = IntroducedBy.objects.filter(user=user).first()
        if first_intro and first_intro.introduced_by:
            first = MarginKeeper(first_intro.introduced_by)
            first.deposit(commission, description=u'月利宝一级淘金', catalog=u"全民淘金")

            income = PhpIncome(user=first_intro.introduced_by, invite=user, level=1,
                               product_id=product_id, amount=_amount['amount__sum'],
                               earning=commission, order_id=first.order_id, paid=True, created_at=timezone.now())
            income.save()

            sec_intro = IntroducedBy.objects.filter(user=first_intro.introduced_by).first()
            if sec_intro and sec_intro.introduced_by:
                second = MarginKeeper(sec_intro.introduced_by)
                second.deposit(commission, description=u'月利宝二级淘金', catalog=u"全民淘金")

                income = PhpIncome(user=sec_intro.introduced_by, invite=user, level=2,
                                   product_id=product_id, amount=_amount['amount__sum'],
                                   earning=commission, order_id=second.order_id, paid=True, created_at=timezone.now())
                income.save()


# TODO 对月利宝进行全民淘金处理, 并加入短信发送统计.
def calc_php_commission(product_id):
    """
    这里每次处理一个满标审核后的标, 只写入记录. 短信发送的时候去统计 散标和月利宝的佣金
    参考:　/wanglibao_redpack/backends.py    function calc_broker_commission
    :param product_id:
    :return:
    """
    if not product_id:
        return

    month_products = MonthProduct.objects.filter(product_id=product_id)
    users = set([product.user for product in month_products])
    if php_commission_exist(product_id):
        return

    start = timezone.datetime(2015, 6, 22, 16, 0, 0, tzinfo=timezone.utc)
    end = timezone.datetime(2016, 6, 30, 15, 59, 59, tzinfo=timezone.utc)
    with transaction.atomic():
        for user in users:
            php_commission(user, product_id, start, end)


def get_php_redis_principle(user_id):
    """
    从redis 或者 api接口 得到用户的待收本金
    :param user_id:
    :return: 1000   代收本金
    """
    try:
        redis_obj = PhpRedisBackend()
        redis_key = 'unpayed_principle_{}'.format(user_id)
        php_unpaid_principle = redis_obj.redis.get(redis_key)
        if php_unpaid_principle:
            return decimal.Decimal(php_unpaid_principle).quantize(Decimal('0.01'))

        else:
            url = settings.PHP_UNPAID_PRINCIPLE
            response = requests.post(url, data={'user_id': user_id}).json()
            try:
                if response.get('total_amount'):
                    return decimal.Decimal(response.get('total_amount')).quantize(Decimal('0.01'))
                else:
                    return 0
            except Exception, e:
                print e
                return 0
    except Exception, e:
        print e
        return 0
