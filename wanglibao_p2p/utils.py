# coding=utf-8

import json
from django.conf import settings
from django.contrib.auth.models import User
from common.utils import product_period_to_days
from common.tools import str_to_utc
from .models import P2PEquity, P2PProduct
from .forms import P2PEquityForm


def save_to_p2p_equity(req_data):
    equity = req_data.get("equity", '')
    if equity:
        equity = json.loads(equity)
        equity['created_at'] = str_to_utc(equity['created_at'])
        if equity['confirm_at']:
            equity['confirm_at'] = str_to_utc(equity['confirm_at'])

        equity_instance = P2PEquity.objects.filter(pk=equity['id']).first()
        if equity_instance:
            equity_form = P2PEquityForm(equity, instance=equity_instance)
        else:
            equity_form = P2PEquityForm(equity)

        if equity_form.is_valid():
            if equity_instance:
                equity_form.save()
            else:
                user = User.objects.get(pk=equity['user'])
                equity['user'] = user
                p2p_product = P2PProduct.objects.get(pk=equity['product'])
                equity['product'] = p2p_product
                equity_instance = P2PEquity()
                for k, v in equity.iteritems():
                    setattr(equity_instance, k, v)
                equity_instance.save()

            response_data = {
                'ret_code': 10000,
                'message': 'success',
            }
        else:
            response_data = {
                'ret_code': 50003,
                'message': equity_form.errors.values()[0][0],
            }
    else:
        response_data = {
            'ret_code': 10112,
            'message': u'缺少equity参数',
        }

    return response_data


def get_user_p2p_total_asset(user):
    # 获取用户p2p总资产

    p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
        u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
    ])

    unpayed_principle = 0
    for equity in p2p_equities:
        if equity.confirm:
            unpayed_principle += equity.unpaid_principal  # 待收本金

    p2p_margin = user.margin.margin  # P2P余额
    p2p_freeze = user.margin.freeze  # P2P投资中冻结金额
    p2p_withdrawing = user.margin.withdrawing  # P2P提现中冻结金额
    other_amount = user.margin.other_amount  # P2P待收本金
    p2p_unpayed_principle = unpayed_principle  # P2P待收本金

    p2p_total_asset = p2p_margin + p2p_freeze + p2p_withdrawing + p2p_unpayed_principle + other_amount

    return p2p_total_asset


def generate_bajinshe_product_data(product):
    product_total_amount = product.total_amount
    product_status = product.status
    pay_method = product.pay_method
    if pay_method == u'等额本息':
        pay_method_code = 3
    elif pay_method == u'按月付息':
        pay_method_code = 1
    elif pay_method == u'日计息一次性还本付息':
        pay_method_code = 2
    elif pay_method == u'到期还本付息':
        pay_method_code = 2
    else:
        pay_method_code = 11

    if product_status == u'正在招标':
        product_status_code = 1
    elif product_status in (u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核'):
        product_status_code = 2
    elif product_status in (u'录标', u'录标完成', u'待审核'):
        product_status_code = 3
    elif product_status == u'还款中':
        product_status_code = 5
    else:
        product_status_code = 0

    if pay_method in [u'等额本息', u'按月付息', u'到期还本付息']:
        period_type = 1
    else:
        period_type = 2

    ordered_amount = product.ordered_amount
    _progress = '%.1f' % (float(ordered_amount) / product_total_amount * 100)
    if _progress == 0 and ordered_amount > 0:
        _progress = 0.1

    product_data = {
        'pid': product.id,
        'productType': 2,
        'productName': product.name[:50],
        'apr': int(product.expected_earning_rate),
        'amount': product_total_amount,
        'pmType': pay_method_code,
        'minIa': 100,
        'progress': _progress,
        'status': product_status_code,
        'period': product.period,
        'periodType': period_type,
    }

    return product_data


p2p_mortgage_type = (u'物流贷', u'过桥周转业务', u'黄金标', u'商圈贷', u'艺术品贷', u'珠宝贷', u'红木贷', u'一般企业贷')
def generate_bisouyi_product_data(product, action):
    pay_method = product.pay_method
    status = 1 if product.status == u'正在招标' else 0

    if action == 'info':
        period = product_period_to_days(pay_method, product.period)

        product_type = product.types
        if product_type in (u'房贷', u'车贷'):
            _attribute = product_type
        else:
            _attribute = u'抵押贷'

        product_data = {
            'pcode': settings.BISOUYI_PCODE,
            'ocode': product.id,
            'ourl': settings.WLB_URL + product.get_h5_url,
            'type': 2,
            'attribute': _attribute,
            'category': product.category,
            'name': product.name[:100],
            'bidmoney': float(product.total_amount),
            'rate': product.expected_earning_rate,
            'period': period,
            'unit': u'1天',
            'progress': product.completion_rate,
            'rdate': product.publish_time.strftime("%Y-%m-%d %H:%M:%S"),
            'edate': product.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            'launchmoney': float(product.limit_per_user),
            'remainmoney': float(product.remain_amount),
            'repayment': pay_method,
            'guarantee': product.warrant_company,
            'detail': product.brief,
            'tradable': status,
            'status': 1,
            'appurl': settings.WLB_URL + product.get_h5_url,
            'weburl': settings.WLB_URL + product.get_pc_url,
        }
    else:
        product_data = {
            'pcode': settings.BISOUYI_PCODE,
            'ocode': product.id,
            'progress': product.completion_rate,
            'remainmoney': float(product.remain_amount),
            'repayment': pay_method,
            'tradable': status,
            'status': 1,
        }

    return product_data
