# coding=utf-8

import json
from django.contrib.auth.models import User
from wanglibao_account.tools import str_to_utc
from .models import P2PEquity, P2PProduct
from .forms import P2PEquityForm


def save_to_p2p_equity(req_data):
    equity = req_data.get("equity", '')
    if equity:
        equity = json.loads(equity)
        equity['created_at'] = str_to_utc(equity['created_at'])
        if equity['created_at']:
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
