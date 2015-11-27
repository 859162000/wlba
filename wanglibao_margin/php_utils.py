# -*- coding: utf-8 -*-
import decimal
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from user_agents import parse

from marketing.models import IntroducedBy
from wanglibao_margin.marginkeeper import MarginKeeper, check_amount
from wanglibao_margin.models import Margin, MarginRecord, MonthProduct
from wanglibao_p2p.models import P2PEquity
from wanglibao_redpack.models import Income
from weixin.util import getAccountInfo


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


def get_user_info(request, session_id):
    """
    get user's base info to php server.
    :param request:
    :param session_id:
    :return:
    userId, 用户 id.
    username, 用户手机号 .
    isDisable, 是否禁用了账户 .
    isRealname, 是否已实名
    总资产
    可用余额
    from_channel, 登录渠道 . 如 :PC
    isAdmin
    """
    user_info = dict()

    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)

    print '######'*100
    print session_id
    print request.session.session_key
    print 'ua_string = ', ua_string
    print 'user agent = ', user_agent

    if session_id == request.session.session_key:
        user = request.user
        account_info = getAccountInfo(user)
        user_info.update(userId=user.pk,
                         username=user.wanglibaouserprofile.phone,
                         realname=user.wanglibaouserprofile.name,
                         isDisable=user.wanglibaouserprofile.frozen,
                         isRealname=0,
                         total_amount=account_info['total_asset'],
                         avaliable_amount=account_info['p2p_margin'],
                         from_channel=ua_string,
                         isAdmin=user.is_superuser)
    else:
        user_info.update(status=False,
                         message=u'session error.')

    return user_info


@csrf_exempt
def get_margin_info(request, user_id):
    """
    :param request:
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
            unpayed_principle = 0
            for equity in p2p_equities:
                if equity.confirm:
                    unpayed_principle += equity.unpaid_principal  # 待收本金

            unpayed_principle = unpayed_principle
            margin = user.margin.margin
            margin_freeze = user.margin.freeze
            margin_withdrawing = user.margin.withdrawing
            total_amount = margin + margin_freeze + margin_withdrawing + unpayed_principle

            return {'state': True, 'margin': margin, 'total_amount': total_amount, 'unpayed_principle': unpayed_principle,
                    'margin_freeze': margin_freeze, 'margin_withdrawing': margin_withdrawing}
    except Exception, e:
        print e

    return {'state': False, 'info': 'user authenticated error!'}


# def commission(user, product_id, equity, start, end):
#     """
#     用户在月利宝购买东西的时候加入佣金.
#     :param user:        购买用户
#     :param product_id:  月利宝产品id
#     :param equity:                      ??????月利宝交易金额
#     :param start:
#     :param end:
#     :return:
#     """
#     _amount = MonthProduct.objects.filter(user=user, product_id=product_id, create_time__gt=start,
#                                           create_time__lt=end).aggregate(Sum('amount'))
#     if _amount['amount__sum'] and _amount['amount__sum'] <= equity:
#         commission = decimal.Decimal(_amount['amount__sum']) * decimal.Decimal("0.003")
#         commission = commission.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
#         first_intro = IntroducedBy.objects.filter(user=user).first()
#         if first_intro and first_intro.introduced_by:
#             first = MarginKeeper(first_intro.introduced_by)
#             first.deposit(commission, catalog=u"全民淘金")
#
#             # 创建一个月利宝对应的P2P产品?????
#             income = Income(user=first_intro.introduced_by, invite=user, level=1,
#                             product=product, amount=_amount['amount__sum'],
#                             earning=commission, order_id=first.order_id, paid=True, created_at=timezone.now())
#             income.save()
#
#             sec_intro = IntroducedBy.objects.filter(user=first_intro.introduced_by).first()
#             if sec_intro and sec_intro.introduced_by:
#                 second = MarginKeeper(sec_intro.introduced_by)
#                 second.deposit(commission, catalog=u"全民淘金")
#
#                 income = Income(user=sec_intro.introduced_by, invite=user, level=2,
#                                 product=product, amount=_amount['amount__sum'],
#                                 earning=commission, order_id=second.order_id, paid=True, created_at=timezone.now())
#                 income.save()
