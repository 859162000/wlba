# -*- coding: utf-8 -*-
import decimal
import logging
from decimal import Decimal

import datetime
from itertools import product

import redis
import requests
import simplejson
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token
from user_agents import parse

from marketing.models import IntroducedBy
from wanglibao import settings
from wanglibao_account.models import Message
from wanglibao_margin.exceptions import MarginLack
from wanglibao_margin.marginkeeper import MarginKeeper, check_amount
from wanglibao_margin.models import Margin, MarginRecord, MonthProduct, PhpRefundRecord
from wanglibao_p2p.models import P2PEquity
from wanglibao_pay.util import fmt_two_amount
from wanglibao_redpack.backends import _decide_device, get_start_end_time, REDPACK_RULE, stamp, _calc_deduct
from wanglibao_redpack.models import PhpIncome, RedPackRecord, RedPackEvent, RedPack
from wanglibao_activity import backends as activity_backends

logger = logging.getLogger('wanglibao_margin')


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


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


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

    def php_freeze(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()

            freeze_before = margin.freeze
            margin_before = margin.margin

            if amount > margin.margin:
                # TODO, check why 201? Magic number sucks, unless its famous, like 404 or 500
                raise MarginLack(u'201')
            margin.margin -= amount
            margin.freeze += amount
            # 交易时从充值未投资中扣除投资金额, 同时将投资金额放入冻结金额中, 当充值未投资金额小于零时为置为 0
            margin_uninvested = margin.uninvested  # 初始未投资余额
            uninvested = margin.uninvested - amount  # 未投资金额 - 投资金额 = 未投资余额计算结果
            margin.uninvested = uninvested if uninvested >= 0 else Decimal('0.00')  # 未投资余额计算结果<0时,结果置0
            margin.uninvested_freeze += amount if uninvested >= 0 else margin_uninvested  # 未投资余额计算结果<0时,未投资冻结金额等于+初始未投资余额
            margin.save()
            catalog = u'交易冻结'
            record = self.tracer(catalog, amount, margin.margin, description,
                                 freeze_before=freeze_before, freeze_after=margin.freeze, margin_before=margin_before)
            return record

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

            margin = Margin.objects.select_for_update().get(user=user)
            margin_before = margin.margin

            if status == 0:
                margin.margin += amount
            else:
                margin.margin -= amount
                margin_uninvested = margin.uninvested  # 初始未投资余额
                uninvested = margin.uninvested - amount  # 未投资金额 - 投资金额 = 未投资余额计算结果
                margin.uninvested = uninvested if uninvested >= 0 else Decimal('0.00')  # 未投资余额计算结果<0时,结果置0
                margin.uninvested_freeze += amount if uninvested >= 0 else margin_uninvested
                # 未投资余额计算结果<0时,未投资冻结金额等于+初始未投资余额
            margin.save()
            record = self.tracer(catalog, amount, margin.margin, description, margin_before=margin_before)
            return record

    def yue_cancel(self, user, amount, description=u'月利宝购买失败', catalog=u'投资失败退回', savepoint=True):
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

            freeze_before = margin.freeze
            margin_before = margin.margin

            if amount > margin.freeze:
                raise MarginLack(u'202')

            margin.margin += amount
            margin.freeze -= amount

            margin.save()
            record = self.tracer(catalog, amount, margin.margin, description,
                                 freeze_before=freeze_before, freeze_after=margin.freeze, margin_before=margin_before)
            return record

    def deposit(self, amount, description=u'月利宝存入', savepoint=True, catalog=u"现金存入"):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()

            margin_before = margin.margin
            margin.margin += amount

            if catalog == u'现金存入':
                margin.uninvested += amount  # 充值未投资金融
            margin.save()
            catalog = catalog
            record = self.tracer(catalog, amount, margin.margin, description, margin_before=margin_before)
            return record

    def tracer(self, catalog, amount, margin_current, description=u'月利宝操作', order_id=None,
               freeze_before=None, freeze_after=None, margin_before=None):
        """
        :param catalog:         操作分类
        :param amount:          操作金额
        :param margin_current:  当前可用金额
        :param description:     描述
        :param order_id:        订单id
        :param freeze_before    操作前冻结金额
        :param freeze_after     操作后冻结金额
        :param margin_before    操作前的可以金额
        :return:
        """
        if not order_id:
            order_id = self.order_id
        trace = MarginRecord(catalog=catalog, amount=amount, margin_current=margin_current, description=description,
                             order_id=order_id, user=self.user, freeze_before=freeze_before, freeze_after=freeze_after,
                             margin_before=margin_before)
        trace.save()
        return trace

    def php_unfreeze(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()

            freeze_before = margin.freeze
            margin_before = margin.margin

            if amount > margin.freeze:
                raise MarginLack(u'202')
            margin.freeze -= amount
            margin.margin += amount
            # 金额解冻时需要同时处理未投资冻结中的金额
            margin_uninvested_freeze = margin.uninvested_freeze
            uninvested_freeze = margin.uninvested_freeze - amount
            margin.uninvested_freeze = uninvested_freeze if uninvested_freeze >= 0 else Decimal('0.00')
            margin.uninvested += amount if uninvested_freeze >= 0 else margin_uninvested_freeze

            margin.save()
            catalog = u'交易解冻'
            record = self.tracer(catalog, amount, margin.margin, description,
                                 freeze_before=freeze_before, freeze_after=margin.freeze, margin_before=margin_before)
            return record

    def php_settle(self, amount, description=u'', savepoint=True):
        amount = Decimal(amount)
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            freeze_before = margin.freeze
            margin_before = margin.margin

            if amount > margin.freeze:
                logger.info('user id: {}, amount:{}, freeze:{} ========'.format(self.user.id, amount, margin.freeze))
                raise MarginLack(u'202')
            margin.freeze -= amount
            uninvested_freeze = margin.uninvested_freeze - amount
            margin.uninvested_freeze = uninvested_freeze if uninvested_freeze >= 0 else Decimal('0.00')
            margin.save()
            catalog = u'投资'       # u'月利宝交易成功扣款' ----> u'投资'
            record = self.tracer(catalog, amount, margin.margin, description,
                                 freeze_before=freeze_before, freeze_after=margin.freeze, margin_before=margin_before)

            # 满标审核时检测活动规则
            activity_backends.check_activity(self.user, 'p2p_audit', 'all', 0, 0)

            return record

    def php_amortize(self, refund_id, user, catalog, amount, description,
                     savepoint=True):
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

                margin_before = margin.margin
                margin.margin += amount

                margin.save()
                try:
                    PhpRefundRecord.objects.get_or_create(
                        refund_id=refund_id, user=user, catalog=catalog, amount=amount,
                        margin_before=margin_before, margin_current=margin.margin, description=description)
                    return 1
                except Exception, e:
                    print e

            # 标的每一期还款完成后,检测该用户还款的本金是否有符合活动的规则,有的话触发活动规则
            try:
                activity_backends.check_activity(user, 'repaid', 'pc', amount)
            except Exception, e:
                logger.debug("check activity on repaid, user: {}, principal: {}, e = {}".format(
                    user, amount, e.message
                ))

    def php_amortize_detail(self, category, principal, interest, t0_interest, coupon_interest, platform_interest,
                            refund_id, savepoint=True):
        """
        针对php 的还款详细写记录
        :param category                 类型, 0 月利宝; 1 债转
        :param principal:           本金
        :param interest:            利息
        :param t0_interest        罚息    penal_interest ---> t0_interest    t+0 补息   # 月利宝平台无罚息
        :param coupon_interest:     红包加息
        :param platform_interest:   平台加息
        :param refund_id:           订单号(唯一值)
        :param savepoint:
        :return:
        """
        check_amount(principal)
        check_amount(interest)
        check_amount(t0_interest)
        principal = Decimal(principal)
        interest = Decimal(interest)
        t0_interest = Decimal(t0_interest)
        coupon_interest = Decimal(coupon_interest)
        platform_interest = Decimal(platform_interest)

        with transaction.atomic(savepoint=savepoint):

            margin = Margin.objects.select_for_update().filter(user=self.user).first()
            margin_before = margin.margin

            if str(category) == '0':
                margin.margin += principal
                self.tracer(u'回款本金', principal, margin.margin,     # u'月利宝本金入账' ---> u'回款本金'
                            u'月利宝本金入账', refund_id, margin_before=margin_before)
                margin_before = margin.margin
                margin.margin += interest
                self.tracer(u'回款收益', interest, margin.margin,       # u'月利宝利息入账' ---> u'回款收益'
                            u'月利宝利息入账', refund_id, margin_before=margin_before)
                if t0_interest > 0:
                    margin_before = margin.margin
                    margin.margin += t0_interest
                    self.tracer(u't+0补息', t0_interest, margin.margin,       # u'月利宝罚息入账' ---> u't+0补息'
                                u'月利宝 t+0补息入账', refund_id, margin_before=margin_before)
                if platform_interest > 0:
                    margin_before = margin.margin
                    margin.margin += platform_interest
                    self.tracer(u'平台加息', platform_interest, margin.margin,     # u'月利宝平台加息入账' ---> u'平台加息'
                                u'月利宝平台加息入账', refund_id, margin_before=margin_before)
                if coupon_interest > 0:
                    margin_before = margin.margin
                    margin.margin += coupon_interest
                    description = u"月利宝加息存入{}元".format(coupon_interest)
                    # self.hike_deposit(coupon_interest, u"加息存入{}元".format(coupon_interest), order_id, savepoint=False)
                    self.tracer(u"加息券收益", coupon_interest, margin.margin,    # u'月利宝加息存入' ---> u'加息券收益'
                                description, refund_id, margin_before=margin_before)

            if str(category) == '1':
                margin_before = margin.margin
                margin.margin += principal
                self.tracer(u'回款本金', principal, margin.margin,
                            u'债转本金入账', refund_id, margin_before=margin_before)
                margin_before = margin.margin
                margin.margin += interest
                self.tracer(u'回款收益', interest, margin.margin,
                            u'债转利息入账', refund_id, margin_before=margin_before)
                if t0_interest > 0:
                    margin_before = margin.margin
                    margin.margin += t0_interest
                    self.tracer(u't+0补息', t0_interest, margin.margin,
                                u'债转t+0补息', refund_id, margin_before=margin_before)
                if platform_interest > 0:
                    margin_before = margin.margin
                    margin.margin += platform_interest
                    self.tracer(u'平台加息', platform_interest, margin.margin,
                                u'债转平台加息入账', refund_id, margin_before=margin_before)
                if coupon_interest > 0:
                    margin_before = margin.margin
                    margin.margin += coupon_interest
                    description = u"债转加息存入{}元".format(coupon_interest)
                    # self.hike_deposit(coupon_interest, u"加息存入{}元".format(coupon_interest), order_id, savepoint=False)
                    self.tracer(u"加息券收益", coupon_interest, margin.margin,
                                description, refund_id, margin_before=margin_before)
            margin.save()


def get_user_info(request, session_id=None, token=None):
    """
    get user's base info to php server.
    :param request:
    :param session_id:
    :param token:
    :return: token:
    from_channel, 登录渠道 . 如 :PC
    isAdmin
    """
    user_info = dict()

    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)

    print 'ua_string = ', ua_string
    print 'user agent = ', user_agent

    user = None

    if session_id and session_id == request.session.session_key:
        user = request.user
    if token:
        token = Token.objects.filter(key=token).first()
        if token:
            user = token.user
        else:
            user = None

    if user:
        if not user.id:
            user_info.update(status=0,
                             message=u'get user error.')
            return user_info

        url = 'https://' + request.get_host() + settings.PHP_UNPAID_PRINCIPLE_BASE
        try:
            if int(request.get_host().split(':')[1]) > 7000:
                url = settings.PHP_APP_INDEX_DATA_DEV
        except Exception, e:
            pass

        margin_info = get_margin_info(user.id, url)

        user_info.update(user_id=user.pk,
                         username=user.wanglibaouserprofile.phone,
                         realname=user.wanglibaouserprofile.name,
                         is_disable=user.wanglibaouserprofile.frozen,
                         is_realname=1 if user.wanglibaouserprofile.id_is_valid else 0,
                         total_amount=margin_info.get('total_amount'),
                         avaliable_amount=margin_info.get('margin'),
                         unpayed_principle=decimal.Decimal(margin_info.get(
                             'unpayed_principle')).quantize(Decimal('0.01')),
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
                         message=u'get user error.')

    return user_info


def get_margin_info(user_id, url=None):
    """
    :param user_id:
    :param url  : 用于根据host 获取 待收本金url
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
            php_principle = get_php_redis_principle(user.pk, url)
            unpaid_principle += php_principle

            margin = user.margin.margin
            margin_freeze = user.margin.freeze
            margin_withdrawing = user.margin.withdrawing
            total_amount = margin + margin_freeze + margin_withdrawing + unpaid_principle

            return {'state': True, 'margin': margin, 'total_amount': total_amount,
                    'unpayed_principle': unpaid_principle, 'margin_freeze': margin_freeze,
                    'margin_withdrawing': margin_withdrawing}
    except Exception, e:
        print e

    return {'state': False, 'info': 'user authenticated error!'}


def php_commission_exist(product_id):
    return PhpIncome.objects.filter(product_id=product_id).exists()
    # return record


def php_commission(user, product_id, start):
    """
    月利宝的表存的是php那边的流水.直接从这获取
    :param user:
    :param product_id:
    :param start:
    :return:
    """
    _amount = MonthProduct.objects.filter(user=user, product_id=product_id, created_at__gt=start,
                                          cancel_status=False).aggregate(Sum('amount'))
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

            # sec_intro = IntroducedBy.objects.filter(user=first_intro.introduced_by).first()
            # if sec_intro and sec_intro.introduced_by:
            #     second = MarginKeeper(sec_intro.introduced_by)
            #     second.deposit(commission, description=u'月利宝二级淘金', catalog=u"全民淘金")
            #
            #     income = PhpIncome(user=sec_intro.introduced_by, invite=user, level=2,
            #                        product_id=product_id, amount=_amount['amount__sum'],
            #                        earning=commission, order_id=second.order_id, paid=True, created_at=timezone.now())
            #     income.save()


def calc_php_commission(product_id):
    """
    这里每次处理一个满标审核后的标, 只写入记录. 短信发送的时候去统计 散标和月利宝的佣金
    参考:　/wanglibao_redpack/backends.py    function calc_broker_commission
    :param product_id:
    :return:
    """
    if not product_id:
        return

    if php_commission_exist(product_id):
        return

    month_products = MonthProduct.objects.filter(product_id=product_id)
    users = set([product.user for product in month_products])

    start = timezone.datetime(2015, 6, 22, 16, 0, 0, tzinfo=timezone.utc)
    # end = timezone.datetime(2016, 6, 30, 15, 59, 59, tzinfo=timezone.utc)
    with transaction.atomic():
        for user in users:
            php_commission(user, product_id, start)


def get_php_redis_principle(user_id, url=None):
    """
    从redis 或者 api接口 得到用户的待收本金
    :param user_id:
    :param url:     增加url 参数, 根据host 确定目标 url
    :return: 1000   代收本金
    """
    try:
        if not url:
            url = settings.PHP_UNPAID_PRINCIPLE
        response = requests.post(url, data={'user_id': user_id}, timeout=3).json()
        try:
            if response.get('total_amount'):
                return decimal.Decimal(response.get('total_amount')).quantize(Decimal('0.01'))
            else:
                return 0
        except Exception, e:
            logger.debug('in get_php_redis_principle, error with : {}'.format(e.message))
            return 0
    except Exception, e:
        logger.debug('in get_php_redis_principle, error with : {}'.format(e.message))
        return 0


def get_php_index_data(url, user_id):
    """
    首页展示信息
    :param url:       = 'https://' + request.get_host() + settings.PHP_APP_INDEX_DATA
    :param user_id:
    :return: {u'code': 1,
              u'data': [{u'paidIncome': 3607.42, u'unPaidIncome': 3616.43, u'yesterdayIncome': 0}]}
    """
    try:
        response = requests.post(url, data={'userId': user_id}, timeout=3).json()
        try:
            if response.get('code') == 1:
                return response.get('data')
            else:
                logger.debug('in get_php_index_data, code != 1')
                return {"yesterdayIncome": 0, "paidIncome": 0, "unPaidIncome": 0}
        except Exception, e:
            logger.debug('in get_php_index_data, error with : {}'.format(e.message))
            return {"yesterdayIncome": 0, "paidIncome": 0, "unPaidIncome": 0}
    except Exception, e:
        logger.debug('in get_php_index_data, error with : {}'.format(e.message))
        return {"yesterdayIncome": 0, "paidIncome": 0, "unPaidIncome": 0}


def get_php_index_data_logout(url):
    """
    未登录时候的首页展示信息
    :param url:       = 'https://' + request.get_host() + settings.PHP_APP_INDEX_DATA
    :param user_id:
    :return: {u'code': 1,
              u'data': [{u'paidIncome': 3607.42, u'unPaidIncome': 3616.43, u'yesterdayIncome': 0}]}
    """
    try:
        response = requests.post(url, data={}, timeout=3).json()
        try:
            if response.get('code') == 1:
                return response.get('data')
            else:
                logger.debug('in get_php_index_data, code != 1')
                return {"repaymentInfoCurrentMonth": 0, "getPaidProject": 0}
        except Exception, e:
            logger.debug('in get_php_index_data, error with : {}'.format(e.message))
            return {"repaymentInfoCurrentMonth": 0, "getPaidProject": 0}
    except Exception, e:
        logger.debug('in get_php_index_data, error with : {}'.format(e.message))
        return {"repaymentInfoCurrentMonth": 0, "getPaidProject": 0}


def get_unread_msgs(user_id):
    """
        获取用户的未读站内信数量
    :param user_id:
    :return:
    """
    ret = dict()
    if not user_id:
        return {}
    if settings.PHP_INSIDE_MESSAGE_LIST_SWITCH == 1:
        try:
            unread_num = Message.objects.filter(target_user=user_id, read_status=False, notice=True).count()
            ret.update(status=1, unread_num=unread_num)
        except Exception, e:
            ret.update(status=0, msg=str(e))
    else:
        response = requests.get(settings.PHP_UNREAD_MESSAGES_COUNT + '?uid={}'.format(user_id))
        res = response.json()
        if res['code'] == 'success':
            ret.update(status=1, unread_num=res['data'])

    return ret


def php_redpacks(user, device_type, period=0, status='available', app_version=''):
    """
    获得月利宝产品对应可用的红包加息券
    月利宝的期限都是月以上的. 传来标需要的周期是几个月, period 整数, 代表最小数量

    :param user:
    :param device_type:
    :param period:
    :param status:
    :param app_version:
    :return:
    """

    if not user.is_authenticated():
        packages = {"available": []}
        return {"ret_code": 0, "packages": packages}

    device_type = _decide_device(device_type)

    # 如果使用了加息券, 散标不能重复使用. 但是月利宝可以重复使用
    if status == "available":
        packages = {"available": []}
        # 红包
        # 包括大于这个周期的红包和等于这个周期的红包. 如 period=3, period_type='month' 和 period=3, period_type='month_gte'
        # 还有天数大于这个周期月的也可以使用
        records = RedPackRecord.objects.filter(user=user, order_id=None, product_id=None)\
            .filter(redpack__event__p2p_types__isnull=True)\
            .filter(Q(redpack__event__period=period, redpack__event__period_type='month') |
                    Q(redpack__event__period__lte=period, redpack__event__period_type='month_gte') |
                    Q(redpack__event__period=period*30, redpack__event__period_type='day') |
                    Q(redpack__event__period__lte=period*30, redpack__event__period_type='day_gte') |
                    # 不限制时间的优惠券
                    Q(Q(redpack__event__period=0)))\
            .exclude(redpack__event__rtype='interest_coupon').order_by('-redpack__event__amount',
                                                                       'redpack__event__unavailable_at')
        for record in records:
            redpack = record.redpack
            if redpack.status == "invalid":
                continue
            event = record.redpack.event
            p2p_types_id = 0
            p2p_types_name = ''

            start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                      record.created_at, event.available_at, event.unavailable_at)

            obj = {"name": event.name, "method": REDPACK_RULE[event.rtype], "amount": event.amount,
                    "id": record.id, "invest_amount": event.invest_amount,
                    "unavailable_at": stamp(end_time), "event_id": event.id,
                    "period": event.period, "period_type": event.period_type,
                    "p2p_types_id": p2p_types_id, "p2p_types_name": p2p_types_name,
                    "highest_amount": event.highest_amount, "order_by": 2}
            if start_time < timezone.now() < end_time:
                if event.apply_platform == "all" or event.apply_platform == device_type or \
                        (device_type in ('ios', 'android') and event.apply_platform == 'app'):
                    if obj['method'] == REDPACK_RULE['percent']:
                        obj['amount'] = obj['amount']/100.0
                    packages['available'].append(obj)

        # 加息券
        # 检测app版本号，小于2.5.2版本不返回加息券列表
        is_show = True
        # if device_type == 'ios' or device_type == 'android':
        #     if app_version < "2.5.3":
        #         is_show = False
        if is_show:
            # 显示加息券, 月利宝可以多次使用加息券
            coupons = RedPackRecord.objects.filter(user=user, order_id=None, product_id=None)\
                .filter(redpack__event__p2p_types__isnull=True)\
                .filter(Q(redpack__event__period=period, redpack__event__period_type='month') |
                        Q(redpack__event__period__lte=period, redpack__event__period_type='month_gte') |
                        Q(redpack__event__period=period*30, redpack__event__period_type='day') |
                        Q(redpack__event__period__lte=period*30, redpack__event__period_type='day_gte') |
                        Q(Q(redpack__event__period=0)))\
                .filter(redpack__event__rtype='interest_coupon').order_by('-redpack__event__amount',
                                                                          'redpack__event__unavailable_at')

            for coupon in coupons:
                if coupon.order_id:
                    continue
                redpack = coupon.redpack
                if redpack.status == 'invalid':
                    continue
                event = coupon.redpack.event

                start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                          coupon.created_at, event.available_at, event.unavailable_at)

                obj = {"name": event.name, "method": REDPACK_RULE[event.rtype], "amount": event.amount,
                       "id": coupon.id, "invest_amount": event.invest_amount,
                       "unavailable_at": stamp(end_time), "event_id": event.id,
                       "period": event.period, "period_type": event.period_type,
                       "highest_amount": event.highest_amount, "order_by": 1}

                if start_time < timezone.now() < end_time:
                    if event.apply_platform == "all" or event.apply_platform == device_type or \
                            (device_type in ('ios', 'android') and event.apply_platform == 'app'):
                        if obj['method'] == REDPACK_RULE['interest_coupon']:
                            obj['amount'] = obj['amount'] / 100.0
                        packages['available'].append(obj)

        # packages['available'].sort(key=lambda x: x['unavailable_at'])
        packages['available'].sort(key=lambda x: x['order_by'], reverse=True)

    return {"ret_code": 0, "packages": packages}


def php_redpack_consume(redpack, amount, user, order_id, device_type, product_id):
    """
    优惠券使用
    :param redpack:
    :param amount:  投资的金额
    :param user:
    :param order_id:    month product id
    :param device_type:
    :param product_id:
    :return:
    """
    amount = fmt_two_amount(amount)
    record = RedPackRecord.objects.filter(user=user, id=redpack).first()
    redpack = record.redpack
    event = redpack.event
    device_type = _decide_device(device_type)

    start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                              record.created_at, event.available_at, event.unavailable_at)
    if not record:
        return {"ret_code": 30171, "message": u"优惠券不存在"}
    if record.order_id or record.product_id:
        return {"ret_code": 30172, "message": u"优惠券已使用"}
    if redpack.status == "invalid":
        return {"ret_code": 30173, "message": u"优惠券已作废"}
    if not start_time < timezone.now() < end_time:
        return {"ret_code": 30174, "message": u"优惠券不可使用"}
    if amount < event.invest_amount:
        return {"ret_code": 30175, "message": u"投资金额不满足优惠券规则%s" % event.invest_amount}
    if event.apply_platform != "all" and (event.apply_platform != device_type or (event.give_platform == 'app' and device_type not in ('ios', 'android'))):
        return {"ret_code": 30176, "message": u"此优惠券只能在%s平台使用" % event.apply_platform}

    rtype = event.rtype
    rule_value = event.amount
    if event.rtype != 'interest_coupon':
        deduct = _calc_deduct(amount, rtype, rule_value, event)
    else:
        deduct = 0

    record.is_month_product = True
    record.order_id = order_id
    record.product_id = product_id
    record.apply_platform = device_type
    record.apply_amount = deduct
    record.apply_at = timezone.now()
    record.save()
    logger.info(u"user : %s,  %s--%s 使用加息券 %s" % (user, event.name, record.id, timezone.now()))

    return {"ret_code": 0, "message": u"ok", "deduct": deduct, "rtype": event.rtype}


def php_redpack_restore(order_id, product_id, amount, user):
    """
    从红包记录获取到使用红包信息
    :param order_id:
    :param product_id:
    :param amount:
    :param user:
    :return:
    """
    if type(amount) != decimal.Decimal:
        amount = fmt_two_amount(amount)
    record = RedPackRecord.objects.filter(is_month_product=True, user=user,
                                          order_id=order_id, product_id=product_id).first()
    if not record:
        return {"ret_code": -1, "message": "redpack not exists"}
    record.apply_platform = ""
    record.apply_at = None
    record.is_month_product = False
    record.order_id = None
    record.product_id = None
    record.save()

    event = record.redpack.event
    rtype = event.rtype
    rule_value = event.amount
    # deduct = event.amount
    deduct = _calc_deduct(amount, rtype, rule_value, event)
    if rtype == "interest_coupon":
        logger.info(u"user : %s,  %s--%s 退回加息券 %s" % (user, event.name, record.id, timezone.now()))
        return {"ret_code": 1, "deduct": deduct}
    else:
        logger.info(u"user : %s,  %s--%s 退回账户 %s" % (user, event.name, record.id, timezone.now()))
        return {"ret_code": 0, "deduct": deduct}


def send_redpacks(event_id, user_ids):
    """
    发送此红包给对应的用户
    :param event_id:         红包活动id
    :param user_ids:           用户list
    :return:
    """
    now = timezone.now()
    red_pack_event = RedPackEvent.objects.filter(pk=event_id, invalid=False,
                                                 give_start_at__lt=now, give_end_at__gt=now).first()

    if not red_pack_event:
        return {'status': 0, 'msg': 'red_pack not valid!'}

    red_pack = RedPack.objects.filter(event=red_pack_event, token='', status='unused').first()
    if not red_pack:
        return {'status': 0, 'msg': 'red_pack can not be send by broadcast!'}

    users = User.objects.filter(id__in=user_ids)
    args_list = []

    for user in users:
        args_list.append(RedPackRecord(redpack=red_pack, user=user))

    try:
        RedPackRecord.objects.bulk_create(args_list)
        return {'status': 1, 'msg': 'success!'}
    except Exception, e:
        return {'status': 0, 'msg': 'send red_packs error: {}'.format(str(e))}
