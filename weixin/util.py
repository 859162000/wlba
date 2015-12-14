# encoding:utf-8
from wanglibao_p2p.models import P2PEquity
from wanglibao_buy.models import FundHoldInfo
from django.template import Template, Context
from django.template.loader import get_template
from .models import WeixinAccounts
from wechatpy import WeChatClient

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def redirectToJumpPage(message):
    url = reverse('jump_page')+'?message=%s'% message
    return HttpResponseRedirect(url)

def sendTemplate(weixin_user, message_template):
    weixin_account = WeixinAccounts.getByOriginalId(weixin_user.account_original_id)
    # account = Account.objects.get(original_id=weixin_user.account_original_id)
    client = WeChatClient(weixin_account.app_id, weixin_account.app_secret)
    client.message.send_template(weixin_user.openid, template_id=message_template.template_id,
                                 top_color=message_template.top_color, data=message_template.data,
                                 url=message_template.url)

def getAccountInfo(user):

    p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
        u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
    ]).select_related('product')
    unpayed_principle = 0
    p2p_total_paid_interest = 0
    p2p_total_unpaid_interest = 0
    p2p_activity_interest = 0
    p2p_total_paid_coupon_interest = 0
    p2p_total_unpaid_coupon_interest = 0
    equity_total = 0
    for equity in p2p_equities:
        equity_total += equity.equity
        if equity.confirm:
            unpayed_principle += equity.unpaid_principal  # 待收本金
            p2p_total_paid_interest += equity.pre_paid_interest  # 累积收益
            p2p_total_unpaid_interest += equity.unpaid_interest  # 待收益
            p2p_total_paid_coupon_interest += equity.pre_paid_coupon_interest  # 加息券已收总收益
            p2p_total_unpaid_coupon_interest += equity.unpaid_coupon_interest  # 加息券待收总收益
            p2p_activity_interest += equity.activity_interest  # 活动收益
    p2p_margin = user.margin.margin  # P2P余额
    p2p_freeze = user.margin.freeze  # P2P投资中冻结金额
    p2p_withdrawing = user.margin.withdrawing  # P2P提现中冻结金额
    p2p_unpayed_principle = unpayed_principle  # P2P待收本金

    p2p_total_asset = p2p_margin + p2p_freeze + p2p_withdrawing + p2p_unpayed_principle

    fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)
    fund_total_asset = 0
    if fund_hold_info.exists():
        for hold_info in fund_hold_info:
            fund_total_asset += hold_info.current_remain_share + hold_info.unpaid_income
    res = {
        'total_asset': float(p2p_total_asset + fund_total_asset),  # 总资产
        'p2p_margin': float(p2p_margin),  # P2P余额
        'p2p_total_unpaid_interest': float(p2p_total_unpaid_interest + p2p_total_unpaid_coupon_interest),  # p2p总待收益
        'p2p_total_paid_interest': float(p2p_total_paid_interest + p2p_activity_interest + p2p_total_paid_coupon_interest),  # P2P总累积收益
        'equity_total':equity_total #投资金额
    }
    return res


def _generate_ajax_template(content, template_name=None):

    context = Context({
        'results': content,
    })

    if template_name:
        template = get_template(template_name)
    else:
        template = Template('<div></div>')

    return template.render(context)
