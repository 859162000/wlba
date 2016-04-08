# coding=utf-8

import json
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from wanglibao_account.tools import str_to_utc
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
    p2p_unpayed_principle = unpayed_principle  # P2P待收本金

    p2p_total_asset = p2p_margin + p2p_freeze + p2p_withdrawing + p2p_unpayed_principle

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
        periodType = 1
    else:
        periodType = 2

    product_data = {
        'pid': product.id,
        'productType': 2,
        'productName': product.name,
        'apr': product.expected_earning_rate,
        'amount': product_total_amount,
        'pmType': pay_method_code,
        'minIa': 100,
        'progress': float('%.1f' % (float(product.ordered_amount) / product_total_amount * 100)),
        'status': product_status_code,
        'period': product.period,
        'periodType': periodType,
    }

    return product_data


def generate_bisouyi_product_data(product, action):
    period = product.period
    pay_method = product.pay_method
    # 根据支付方式判定标周期的单位（天/月）,如果是单位为月则转换为天
    if pay_method in [u'等额本息', u'按月付息', u'到期还本付息']:
        period = relativedelta(months=period).days

    status = 1 if product.status == u'正在招标' else 0

    if action == 'info':
        product_data = {
            'pcode': settings.BISOUYI_PCODE,
            'ocode': product.id,
            'ourl': settings.WLB_URL + product.get_h5_url,
            'type': 2,
            'attribute': '', # FixMe
            'category': product.category,
            'name': product.name,
            'bidmoney': float(product.total_amount),
            'rate': product.expected_earning_rate, # FixMe
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
