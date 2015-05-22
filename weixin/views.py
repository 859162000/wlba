# encoding:utf-8
from django.views.generic import View, TemplateView, RedirectView
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login
from django.template import Template, Context
from django.template.loader import get_template
from django.db.models import Q
from django.shortcuts import render_to_response, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from wanglibao_account.forms import EmailOrPhoneAuthenticationForm
from wanglibao_buy.models import FundHoldInfo
from wanglibao_banner.models import Banner
from wanglibao_p2p.models import P2PProduct, P2PEquity
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_margin.models import Margin
from wanglibao_redpack import backends
from wanglibao_rest import utils
# from wanglibao_pay import third_pay, trade_record
from wanglibao_pay.models import Bank
from weixin.wechatpy import WeChatClient, parse_message, create_reply
from weixin.wechatpy.replies import TransferCustomerServiceReply
from weixin.wechatpy.utils import check_signature
from weixin.wechatpy.exceptions import InvalidSignatureException, WeChatException
from weixin.wechatpy.oauth import WeChatOAuth
from weixin.common.decorators import weixin_api_error
from weixin.common.wechat import WeixinAccounts
from weixin.common.wxpay import JSWXpay
from .models import Account, WeixinUser
from .common.wechat import tuling
from decimal import Decimal
import datetime
import json
import time
import uuid
import urllib


account_main = WeixinAccounts.get('main')
js_wxpay = JSWXpay(
    appid=account_main.app_id,
    mch_id=account_main.mch_id,
    key=account_main.key,
    ip='119.254.110.30',
    notify_url='http://pay.pythink.com/weixin/pay/notify/',
    appsecret=account_main.app_secret
)


class ConnectView(View):
    account = None

    def check_signature(self, request, id):
        try:
            self.account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            return False

        try:
            check_signature(
                self.account.token,
                request.GET.get('signature'),
                request.GET.get('timestamp'),
                request.GET.get('nonce')
            )
        except InvalidSignatureException:
            return False

        return True

    def get(self, request, id):
        if not self.check_signature(request, id):
            return HttpResponseForbidden()

        return HttpResponse(request.GET.get('echostr'))

    def post(self, request, id):
        if not self.check_signature(request, id):
            return HttpResponseForbidden()

        msg = parse_message(request.body)

        # 更新公众号原始ID 更新公众号关注者数据
        self.account.weixin_original_id = msg.target
        WeixinUser.objects.get_or_create(openid=msg.source, account_original_id=msg.target)

        if msg.type == 'text':
            # 自动回复  5000次／天
            reply = tuling(msg)
            # 多客服转接
            # reply = TransferCustomerServiceReply(message=msg)
        else:
            reply = create_reply(u'更多功能，敬请期待！', msg)

        return HttpResponse(reply.render())

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ConnectView, self).dispatch(request, *args, **kwargs)


class WeixinJoinView(View):
    account = None

    def check_signature(self, request, account_key):
        account = WeixinAccounts.get(account_key)
        try:
            check_signature(
                account.token,
                request.GET.get('signature'),
                request.GET.get('timestamp'),
                request.GET.get('nonce')
            )
        except InvalidSignatureException:
            return False

        return True

    def get(self, request, account_key):
        if not self.check_signature(request, account_key):
            return HttpResponseForbidden()

        return HttpResponse(request.GET.get('echostr'))

    def post(self, request, account_key):
        if not self.check_signature(request, account_key):
            return HttpResponseForbidden()

        msg = parse_message(request.body)

        if msg.type == 'text':
            # 自动回复  5000次／天
            reply = tuling(msg)
            # 多客服转接
            # reply = TransferCustomerServiceReply(message=msg)
        else:
            reply = create_reply(u'更多功能，敬请期待！', msg)

        return HttpResponse(reply.render())

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WeixinJoinView, self).dispatch(request, *args, **kwargs)


class WeixinJsapiConfig(APIView):
    permission_classes = ()
    http_method_names = ['get']

    @weixin_api_error
    def get(self, request):
        try:
            account = Account.objects.first()
        except Account.DoesNotExist:
            data = {'errcode': 1, 'errmsg': 'account does not exist'}
            return Response(data, status=400)

        noncestr = uuid.uuid1().hex
        timestamp = str(int(time.time()))
        url = (request.META.get('HTTP_REFERER') or '').split('#')[0]

        # app_id = account_main.app_id
        # signature = account_main.weixin_client.jsapi.get_jsapi_signature(
        #     noncestr,
        #     account_main.jsapi_ticket,
        #     timestamp,
        #     url
        # )

        app_id = account.app_id
        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        signature = client.jsapi.get_jsapi_signature(noncestr, account.jsapi_ticket, timestamp, url)

        data = {
            'appId': app_id,
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'signature': signature
        }
        return Response(data)


class WeixinLogin(TemplateView):
    template_name = 'weixin_login.jade'

    def get_context_data(self, **kwargs):
        context = super(WeixinLogin, self).get_context_data(**kwargs)
        code = self.request.GET.get('code')

        if code:
            account_id = self.request.GET.get('state')
            try:
                account = Account.objects.get(pk=account_id)
            except Account.DoesNotExist:
                return HttpResponseNotFound()

            try:
                oauth = WeChatOAuth(account.app_id, account.app_secret)
                res = oauth.fetch_access_token(code)
                account.oauth_access_token = res.get('access_token')
                account.oauth_access_token_expires_in = res.get('expires_in')
                account.oauth_refresh_token = res.get('refresh_token')
                account.save()
                WeixinUser.objects.get_or_create(openid=res.get('openid'))
                context['openid'] = res.get('openid')
            except WeChatException, e:
                pass

        return context


class WeixinLoginApi(APIView):
    permission_classes = ()
    http_method_names = ['post']

    def _form(self, request):
        return EmailOrPhoneAuthenticationForm(request, data=request.POST)

    def post(self, request):
        form = self._form(request)

        if form.is_valid():
            user = form.get_user()

            try:
                openid = request.POST.get('openid')
                weixin_user = WeixinUser.objects.get(openid=openid)
                weixin_user.user = user
                weixin_user.save()
            except WeixinUser.DoesNotExist:
                pass

            auth_login(request, user)
            request.session.set_expiry(1800)
            data = {'nickname': user.wanglibaouserprofile.nick_name}
            return Response(data)

        return Response(form.errors, status=400)


class WeixinOauthLoginRedirect(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            account = Account.objects.first()
        except Account.DoesNotExist:
            raise Http404()

        oauth = WeChatOAuth(
            app_id=account.app_id,
            app_secret=account.app_secret,
            redirect_uri=self.request.build_absolute_uri(reverse('weixin_login')),
            scope='snsapi_base',
            state=str(account.id)
        )

        return oauth.authorize_url


class WeixinPayTest(TemplateView):
    template_name = 'pay_test.html'

    def get_context_data(self, **kwargs):
        context = super(WeixinPayTest, self).get_context_data(**kwargs)
        code = self.request.GET.get('code')
        openid = js_wxpay.generate_openid(code)
        context['openid'] = openid
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.GET.get('code'):
            info_dict = {
                'redirect_uri': request.build_absolute_uri(reverse('weixin_pay_test')),
                'state': '123',
            }
            url = js_wxpay.generate_redirect_url(info_dict)
            return HttpResponseRedirect(url)

        return super(WeixinPayTest, self).dispatch(request, *args, **kwargs)


class WeixinPayOrder(APIView):
    permission_classes = ()
    http_method_names = ['post']

    def post(self, request):
        product = {
            'attach': u'网利宝微信支付测试1分',
            'body': u'网利宝微信支付测试1分',
            'out_trade_no': uuid.uuid1().hex,
            'total_fee': 0.01,
        }
        data = js_wxpay.generate_jsapi(product, request.POST.get('openid'))
        return Response(data)


class WeixinPayNotify(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        xml_str = request.body
        print 'xml_str: {}'.format(xml_str)
        ret, ret_dict = js_wxpay.verify_notify(xml_str)
        print 'ret: {}'.format(ret)
        print 'ret_dict: ', ret_dict
        # 在这里添加订单更新逻辑
        if ret:
            ret_dict = {
                'return_code': 'SUCCESS',
                'return_msg': 'OK',
            }
            ret_xml = js_wxpay.generate_notify_resp(ret_dict)
        else:
            ret_dict = {
                'return_code': 'FAIL',
                'return_msg': 'verify error',
            }
            ret_xml = js_wxpay.generate_notify_resp(ret_dict)

        print 'ret_xml: {}'.format(ret_xml)
        return HttpResponse(ret_xml)



class P2PListView(TemplateView):
    template_name = 'weixin_list.jade'

    def get_context_data(self, **kwargs):
        p2p_lists = P2PProduct.objects.filter(hide=False).filter(status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
        ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).order_by('-priority', '-publish_time')[:10]

        banner = Banner.objects.filter(device='weixin', type='banner', is_used=True).order_by('-priority').first()

        return {
            'p2p_lists': p2p_lists,
            'banner': banner,
        }


def _generate_ajax_template(content, template_name=None):

    context = Context({
        'p2p_lists': content,
    })

    if template_name:
        template = get_template(template_name)
    else:
        template = Template('<div></div>')

    return template.render(context)


class P2PListWeixin(APIView):
    permission_classes = ()

    @property
    def allowed_methods(self):
        return ['GET', 'POST']

    def get(self, request):

        page = request.GET.get('page', 1)
        pagesize = request.GET.get('pagesize', 10)
        page = int(page)
        pagesize = int(pagesize)

        p2p_lists = P2PProduct.objects.filter(hide=False)\
            .filter(status__in=[u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'])\
            .exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标'))\
            .order_by('-priority', '-publish_time')[(page-1)*pagesize:page*pagesize]

        html_data = _generate_ajax_template(p2p_lists, 'include/ajax/ajax_list.jade')

        return Response({
            'html_data': html_data,
            'page': page,
            'pagesize': pagesize,
        })


class P2PDetailView(TemplateView):

    def get_template_names(self):
        template = self.kwargs['template']
        if template == 'calculator':
            template_name = 'weixin_calculator.jade'
        elif template == 'buy':
            template_name = 'weixin_buy.jade'
        else:
            template_name = 'weixin_detail.jade'

        return template_name

    def get_context_data(self, id, **kwargs):
        context = super(P2PDetailView, self).get_context_data(**kwargs)

        try:
            p2p = P2PProduct.objects.select_related('activity').exclude(status=u'流标').exclude(status=u'录标')\
                .get(pk=id, hide=False)

            if p2p.soldout_time:
                end_time = p2p.soldout_time
            else:
                end_time = p2p.end_time
        except P2PProduct.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        terms = get_amortization_plan(p2p.pay_method).generate(p2p.total_amount,
                                                               p2p.expected_earning_rate / 100,
                                                               datetime.datetime.now(),
                                                               p2p.period)
        total_earning = terms.get('total') - p2p.total_amount
        total_fee_earning = 0

        if p2p.activity:
            total_fee_earning = Decimal(p2p.total_amount * p2p.activity.rule.rule_amount *
                                        (Decimal(p2p.period) / Decimal(12))).quantize(Decimal('0.01'))

        user_margin = 0
        current_equity = 0
        redpack = None
        user = self.request.user
        if user.is_authenticated():
            user_margin = user.margin.margin
            equity_record = p2p.equities.filter(user=user).first()
            if equity_record is not None:
                current_equity = equity_record.equity

            device = utils.split_ua(self.request)
            redpack = backends.list_redpack(user, 'available', device['device_type'])

        orderable_amount = min(p2p.limit_amount_per_user - current_equity, p2p.remain)
        total_buy_user = P2PEquity.objects.filter(product=p2p).count()

        amount = self.request.GET.get('amount', 0)
        amount_profit = self.request.GET.get('amount_profit', 0)
        print self.request.GET
        next = self.request.GET.get('next', '')

        context.update({
            'p2p': p2p,
            'end_time': end_time,
            'orderable_amount': orderable_amount,
            'total_earning': total_earning,
            'current_equity': current_equity,
            'attachments': p2p.attachment_set.all(),
            'total_fee_earning': total_fee_earning,
            'total_buy_user': total_buy_user,
            'margin': float(user_margin),
            'amount': float(amount),
            'redpack': redpack,
            'next': next,
            'amount_profit': amount_profit,
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            if self.kwargs['template'] == 'buy':
                amount = request.GET.get('amount', '')
                amount_profit = request.GET.get('amount_profit', '')
                next_str = '?amount=%s&amount_profit=%s' % (amount, amount_profit)
                redirect_str = '/weixin/login/?next=/weixin/view/buy/%s/%s' % (self.kwargs['id'], urllib.quote(next_str))
                return HttpResponseRedirect(redirect_str)
        return super(P2PDetailView, self).dispatch(request, *args, **kwargs)


class WeixinAccountHome(TemplateView):
    template_name = 'weixin_account.jade'

    def get_context_data(self, **kwargs):
        user = self.request.user

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        unpayed_principle = 0
        p2p_total_paid_interest = 0
        p2p_total_unpaid_interest = 0
        p2p_total_interest = 0
        p2p_activity_interest = 0
        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal  # 待收本金
                p2p_total_paid_interest += equity.pre_paid_interest  # 累积收益
                p2p_total_unpaid_interest += equity.unpaid_interest  # 待收益
                p2p_total_interest += equity.pre_total_interest  # 总收益
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

        banner = Banner.objects.filter(device='weixin', type='banner', is_used=True).order_by('-priority').first()

        return {
            'total_asset': p2p_total_asset + fund_total_asset,  # 总资产
            'p2p_total_asset': p2p_total_asset,  # p2p总资产
            'p2p_margin': p2p_margin,  # P2P余额
            'p2p_freeze': p2p_freeze,  # P2P投资中冻结金额
            'p2p_withdrawing': p2p_withdrawing,  # P2P提现中冻结金额
            'p2p_unpayed_principle': p2p_unpayed_principle,  # P2P待收本金
            'p2p_total_unpaid_interest': p2p_total_unpaid_interest,  # p2p总待收益
            'p2p_total_paid_interest': p2p_total_paid_interest + p2p_activity_interest,  # P2P总累积收益
            'p2p_total_interest': p2p_total_interest,  # P2P总收益
            'banner': banner,
        }


class WeixinRecharge(TemplateView):
    template_name = 'weixin_recharge.jade'

    def get_context_data(self, **kwargs):

        banks = Bank.get_kuai_deposit_banks()

        return {
            'banks': banks,
        }


class WeixinRechargeSecond(TemplateView):
    template_name = 'weixin_recharge_second.jade'

    def get_context_data(self, **kwargs):
        card_no = self.request.GET.get('card_no', '')
        gate_id = self.request.GET.get('gate_id', '')
        amount = self.request.GET.get('amount', 0)

        try:
            bank = Bank.objects.filter(gate_id=gate_id).first()
        except:
            bank = None

        context = {
            'card_no': card_no,
            'gate_id': gate_id,
            'amount': amount,
            'bank': bank,
        }
        return context

