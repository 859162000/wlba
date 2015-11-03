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
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from wanglibao_account.forms import EmailOrPhoneAuthenticationForm
from wanglibao_buy.models import FundHoldInfo
from wanglibao_banner.models import Banner
from wanglibao_p2p.models import P2PProduct, P2PEquity, Attachment
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_margin.models import Margin
from wanglibao_redpack import backends
from wanglibao_rest import utils
# from wanglibao_pay import third_pay, trade_record
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from wanglibao_pay.models import Bank
from weixin.wechatpy import WeChatClient, parse_message, create_reply
from weixin.wechatpy.replies import TransferCustomerServiceReply
from weixin.wechatpy.utils import check_signature
from weixin.wechatpy.exceptions import InvalidSignatureException, WeChatException,WeChatOAuthException
from wanglibao_reward.models import WanglibaoUserGift, WanglibaoWeixinRelative, WanglibaoActivityGift
from weixin.wechatpy.oauth import WeChatOAuth
from weixin.common.decorators import weixin_api_error
from weixin.common.wx import generate_js_wxpay
from .models import Account, WeixinUser, WeixinAccounts, AuthorizeInfo
from .common.wechat import tuling
from decimal import Decimal
from wanglibao_pay.models import Card
from marketing.models import Channels
from marketing.utils import get_channel_record
import datetime
import base64
import json
import time
import uuid
import urllib
import math
import logging
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from wanglibao_p2p.views import get_p2p_list
from wanglibao_redis.backend import redis_backend
import pickle
from rest_framework import renderers

logger = logging.getLogger('wanglibao_reward')


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
        if settings.ENV == settings.ENV_DEV:
            request.session['account_key'] = 'test'
            account = WeixinAccounts.get('test')
        else:
            request.session['account_key'] = 'sub_1'
            account = WeixinAccounts.get('sub_1')

        noncestr = uuid.uuid1().hex
        timestamp = str(int(time.time()))
        url = (request.META.get('HTTP_REFERER') or '').split('#')[0]

        app_id = account.app_id
        signature = account.weixin_client.jsapi.get_jsapi_signature(
            noncestr,
            account.jsapi_ticket,
            timestamp,
            url
        )

        data = {
            'appId': app_id,
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'signature': signature
        }
        return Response(data)


class WeixinLogin(TemplateView):
    template_name = 'weixin_login_new.jade'

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
        next = self.request.GET.get('next', '')
        return {
            'context' : context,
            'next'   : next
            }


class WeixinRegister(TemplateView):
    template_name = 'weixin_regist_new.jade'

    def get_context_data(self, **kwargs):
        token = self.request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, '')
        token_session = self.request.session.get(settings.PROMO_TOKEN_QUERY_STRING, '')
        if token:
            token = token
        elif token_session:
            token = token_session
        else:
            token = 'weixin'

        if token:
            channel = get_channel_record(token)
        else:
            channel = None
        phone = self.request.GET.get('phone', 0)
        next = self.request.GET.get('next', '')
        return {
            'token': token,
            'channel': channel,
            'phone': phone,
            'next' : next
        }


class WeixinLoginAPI(APIView):
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
        js_wxpay = generate_js_wxpay(self.request)
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
            js_wxpay = generate_js_wxpay(request)
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
        js_wxpay = generate_js_wxpay(request)
        data = js_wxpay.generate_jsapi(product, request.POST.get('openid'))
        return Response(data)


class WeixinPayNotify(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        js_wxpay = generate_js_wxpay(request)
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
        p2p_products = []

        p2p_done_list, p2p_full_list, p2p_repayment_list, p2p_finished_list = get_p2p_list()

        p2p_products.extend(p2p_done_list)
        p2p_products.extend(p2p_full_list)
        p2p_products.extend(p2p_repayment_list)
        p2p_products.extend(p2p_finished_list)

        limit = 10
        paginator = Paginator(p2p_products, limit)
        page = self.request.GET.get('page')

        try:
            p2p_products = paginator.page(page)
        except PageNotAnInteger:
            p2p_products = paginator.page(1)
        except Exception:
            p2p_products = paginator.page(paginator.num_pages)

        banner = Banner.objects.filter(device='weixin', type='banner', is_used=True).order_by('-priority')

        return {
            'results': p2p_products[:10],
            'banner': banner,
        }


def _generate_ajax_template(content, template_name=None):

    context = Context({
        'results': content,
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

        p2p_products = []

        p2p_done_list, p2p_full_list, p2p_repayment_list, p2p_finished_list = get_p2p_list()

        p2p_products.extend(p2p_done_list)
        p2p_products.extend(p2p_full_list)
        p2p_products.extend(p2p_repayment_list)
        p2p_products.extend(p2p_finished_list)

        page = request.GET.get('page', 1)
        pagesize = request.GET.get('pagesize', 10)
        page = int(page)
        pagesize = int(pagesize)

        paginator = Paginator(p2p_products, pagesize)

        try:
            p2p_products = paginator.page(page)
        except PageNotAnInteger:
            p2p_products = paginator.page(1)
        except Exception:
            p2p_products = paginator.page(paginator.num_pages)

        html_data = _generate_ajax_template(p2p_products, 'include/ajax/ajax_list.jade')

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

        # try:
        #     p2p = P2PProduct.objects.select_related('activity').exclude(status=u'流标').exclude(status=u'录标')\
        #         .get(pk=id, hide=False)
        #
        #     if p2p.soldout_time:
        #         end_time = p2p.soldout_time
        #     else:
        #         end_time = p2p.end_time
        # except P2PProduct.DoesNotExist:
        #     raise Http404(u'您查找的产品不存在')
        cache_backend = redis_backend()
        p2p = cache_backend.get_cache_p2p_detail(id)
        if not p2p:
            raise Http404(u'您查找的产品不存在')

        if p2p['soldout_time']:
            end_time = p2p['soldout_time']
        else:
            end_time = p2p['end_time']

        terms = get_amortization_plan(p2p['pay_method']).generate(p2p['total_amount'],
                                                               p2p['expected_earning_rate'] / 100,
                                                               datetime.datetime.now(),
                                                               p2p['period'])
        total_earning = terms.get('total') - p2p['total_amount']
        total_fee_earning = 0

        if p2p['activity']:
            total_fee_earning = Decimal(p2p['total_amount'] * p2p['activity']['activity_rule_amount'] *
                                        (Decimal(p2p['period']) / Decimal(12))).quantize(Decimal('0.01'))

        user_margin = 0
        current_equity = 0
        redpacks = []
        user = self.request.user
        if user.is_authenticated():
            user_margin = user.margin.margin
            equity_record = P2PEquity.objects.filter(product=p2p['id']).filter(user=user).first()
            if equity_record is not None:
                current_equity = equity_record.equity

            device = utils.split_ua(self.request)
            result = backends.list_redpack(user, 'available', device['device_type'], p2p['id'])
            redpacks = result['packages'].get('available', [])

        orderable_amount = min(p2p['limit_amount_per_user'] - current_equity, p2p['remain'])
        total_buy_user = P2PEquity.objects.filter(product=p2p['id']).count()

        amount = self.request.GET.get('amount', 0)
        amount_profit = self.request.GET.get('amount_profit', 0)
        next = self.request.GET.get('next', '')
        context.update({
            'p2p': p2p,
            'end_time': end_time,
            'orderable_amount': orderable_amount,
            'total_earning': total_earning,
            'current_equity': current_equity,
            'attachments': p2p['attachments'],
            'total_fee_earning': total_fee_earning,
            'total_buy_user': total_buy_user,
            'margin': float(user_margin),
            'amount': float(amount),
            'redpacks': redpacks,
            'next': next,
            'amount_profit': amount_profit,
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            if self.kwargs['template'] == 'buy':
                #未登录状态下buy模板不需要取 amount 和 amount_profit
                #amount = request.GET.get('amount', '')
                #amount_profit = request.GET.get('amount_profit', '')
                #next_str = '?amount=%s&amount_profit=%s' % (amount, amount_profit)
                redirect_str = '/weixin/login/?next=/weixin/view/buy/%s/' % (self.kwargs['id'],)
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
        next = self.request.GET.get('rechargeNext', '')
        return {
            'banks': banks,
            'next' : next,
        }


class WeixinRechargeSecond(TemplateView):
    template_name = 'weixin_recharge_second.jade'

    def get_context_data(self, **kwargs):
        card_no = self.request.GET.get('card_no', '')
        gate_id = self.request.GET.get('gate_id', '')
        amount = self.request.GET.get('amount', 0)
        user = self.request.user.wanglibaouserprofile
        try:
            bank = Bank.objects.filter(gate_id=gate_id).first()
        except:
            bank = None
        next = self.request.GET.get('rechargeNext', '')
        context = {
            'card_no': card_no,
            'gate_id': gate_id,
            'amount': amount,
            'bank': bank,
            'user': user,
            'next': next,
        }
        return context


class WeixinTransaction(TemplateView):
    template_name = 'weixin_transaction.jade'

    def get_template_names(self):
        status = self.kwargs['status']
        if status == 'buying':
            template_name = 'weixin_transaction_buying.jade'
        elif status == 'finished':
            template_name = 'weixin_transaction_finished.jade'
        else:
            template_name = 'weixin_transaction.jade'

        return template_name

    def get_context_data(self, status, **kwargs):
        if status not in ['repaying', 'buying', 'finished']:
            return Response({'ret_code': 20400, 'message': u'标的状态错误'})
        has_link = False
        if status == 'repaying':
            has_link = True
            p2p_status = u'还款中'
        elif status == 'finished':
            p2p_status = u'已完成'
        else:
            p2p_status = u'正在招标'
        if status == 'buying':
            p2p_equities = P2PEquity.objects.filter(user=self.request.user).filter(product__status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'正在招标',
            ]).select_related('product')[:10]
        else:
            p2p_equities = P2PEquity.objects.filter(user=self.request.user).filter(product__status=p2p_status) \
                .select_related('product')[:10]

        p2p_records = [{
            'equity_created_at': timezone.localtime(equity.created_at).strftime("%Y-%m-%d %H:%M:%S"),  # 投标时间
            'equity_product_short_name': equity.product.short_name,  # 产品名称
            'equity_product_expected_earning_rate': equity.product.expected_earning_rate,  # 年化收益(%)
            'equity_product_period': equity.product.period,  # 产品期限(月)*
            'equity_equity': float(equity.equity),  # 用户所持份额(投资金额)
            'equity_product_display_status': equity.product.display_status,  # 状态
            'equity_term': equity.term,  # 还款期
            'equity_product_amortization_count': equity.product.amortization_count,  # 还款期数
            'equity_paid_interest': float(equity.pre_paid_interest + equity.pre_paid_coupon_interest),  # 单个已经收益
            'equity_total_interest': float(equity.pre_total_interest + equity.pre_total_coupon_interest),  # 单个预期收益
            'equity_will_interest': float(equity.pre_total_interest - equity.pre_paid_interest + equity.unpaid_coupon_interest),
            'equity_contract': 'https://%s/api/p2p/contract/%s/' % (
                self.request.get_host(), equity.product.id),  # 合同
            'product_id': equity.product_id,
            'has_link': has_link,
        } for equity in p2p_equities]

        return {
            'results': p2p_records
        }


class WeixinP2PRecordAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        get_status = request.GET.get('status', 'repaying')
        if get_status not in ['repaying', 'buying', 'finished']:
            return Response({'ret_code': 20400, 'message': u'标的状态错误'})
        has_link = False
        if get_status == 'repaying':
            has_link = True
            p2p_status = u'还款中'
        elif get_status == 'finished':
            p2p_status = u'已完成'
        else:
            p2p_status = u'正在招标'
        page = request.GET.get('page', 1)
        pagesize = request.GET.get('pagesize', 10)
        page = int(page)
        pagesize = int(pagesize)

        if get_status == 'buying':
            p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'正在招标',
            ]).select_related('product')[(page-1)*pagesize:page*pagesize]
        else:
            p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status=p2p_status)\
                .select_related('product')[(page-1)*pagesize:page*pagesize]

        p2p_records = [{
             'equity_created_at': timezone.localtime(equity.created_at).strftime("%Y-%m-%d %H:%M:%S"),  # 投标时间
             'equity_product_short_name': equity.product.short_name,  # 产品名称
             'equity_product_expected_earning_rate': equity.product.expected_earning_rate,  # 年化收益(%)
             'equity_product_period': equity.product.period,  # 产品期限(月)*
             'equity_equity': float(equity.equity),  # 用户所持份额(投资金额)
             'equity_product_display_status': equity.product.display_status,  # 状态
             'equity_term': equity.term,  # 还款期
             'equity_product_amortization_count': equity.product.amortization_count,  # 还款期数
             'equity_paid_interest': float(equity.pre_paid_interest),  # 单个已经收益
             'equity_total_interest': float(equity.pre_total_interest),  # 单个预期收益
             'equity_contract': 'https://%s/api/p2p/contract/%s/' % (
                 request.get_host(), equity.product.id),  # 合同
             'product_id': equity.product_id,
             'has_link': has_link,
        } for equity in p2p_equities]

        html_data = _generate_ajax_template(p2p_records, 'include/ajax/ajax_transaction.jade')

        return Response({
            'html_data': html_data,
            'page': page,
            'pagesize': pagesize,
        })


class WeixinAccountSecurity(TemplateView):
    template_name = 'weixin_security.jade'

    def get_context_data(self, **kwargs):
        p2p_cards = Card.objects.filter(user__exact=self.request.user).count()
        return {
            'p2p_cards': p2p_cards,
        }


class WeixinAccountBankCard(TemplateView):
    template_name = 'weixin_bankcard.jade'

    def get_context_data(self, **kwargs):
        p2p_cards = Card.objects.filter(user__exact=self.request.user)
        return {
            'p2p_cards': p2p_cards,
        }


class WeixinAccountBankCardAdd(TemplateView):
    template_name = 'weixin_bankcard_add.jade'

    def get_context_data(self, **kwargs):
        banks = Bank.get_withdraw_banks()
        return {
            'banks': banks,
        }

import time
class AuthorizeCode(APIView):
    permission_classes = ()

    def get(self, request):
        account_id = self.request.GET.get('state')
        try:
            account = Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            return HttpResponseNotFound()
        auth = request.GET.get('auth')
        redirect_uri = settings.WEIXIN_CALLBACK_URL + reverse("weixin_authorize_user_info")
        count = 0
        for key in request.GET.keys():
            if key == u'state':
                continue
            if count == 0:
                redirect_uri += '?%s=%s'%(key, request.GET.get(key))
            else:
                redirect_uri += "&%s=%s"%(key, request.GET.get(key))
            count += 1

        # print redirect_uri
        if auth and auth=='1':
            oauth = WeChatOAuth(account.app_id, account.app_secret, redirect_uri=redirect_uri, scope='snsapi_userinfo', state=account_id)
        else:
            oauth = WeChatOAuth(account.app_id, account.app_secret, redirect_uri=redirect_uri, state=account_id)
        # print oauth.authorize_url
        return redirect(oauth.authorize_url)


class AuthorizeUser(APIView):
    permission_classes = ()
    def get(self, request):
        account_id = self.request.GET.get('state')
        try:
            account = Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            return HttpResponseNotFound()
        redirect_uri = self.request.GET.get('redirect_uri')
        redirect_url = ''
        if redirect_uri:
            redirect_url = urllib.unquote(redirect_uri)
        if not redirect_url:
            return Response({'errcode':-1,  'errmsg':'need a redirect_uri'})
        code = request.GET.get('code')
        oauth = WeChatOAuth(account.app_id, account.app_secret, )
        if code:
            try:
                res = oauth.fetch_access_token(code)
            except WeChatException, e:
                return Response({'errcode':e.errcode, 'errmsg':e.errmsg})
            openid = res.get('openid')
            w_user = WeixinUser.objects.filter(openid=openid).first()
            save_user = False

            if not w_user:
                w_user = WeixinUser()
                w_user.account_original_id = account.original_id
                w_user.openid = openid
                save_user = True

            if w_user.account_original_id != account.original_id:
                w_user.account_original_id = account.original_id
                save_user = True

            if not w_user.auth_info:
                auth_info = AuthorizeInfo()
                auth_info.access_token = res.get('access_token')
                auth_info.access_token_expires_at = Account._now() + datetime.timedelta(seconds=res.get('expires_in') - 60)
                auth_info.refresh_token = res.get('refresh_token')
                auth_info.save()
                w_user.auth_info = auth_info
                save_user = True
            else:
                w_user.auth_info.access_token = res.get('access_token')
                w_user.auth_info.access_token_expires_at = Account._now() + datetime.timedelta(seconds=res.get('expires_in') - 60)
                w_user.auth_info.refresh_token = res.get('refresh_token')
                w_user.auth_info.save()
            if save_user:
                w_user.save()

            appendkeys = []
            for key in request.GET.keys():
                if key == u'state' or key == u'code':
                    continue
                appendkeys.append(key)

            if redirect_url.find('?') == -1:
                redirect_url += '?openid=%s'%openid
            else:
                redirect_url += '&openid=%s'%openid
            for key in appendkeys:
                redirect_url += '&%s=%s'%(key, request.GET.get(key))
            return redirect(redirect_url)

        return Response({'errcode':-2, 'errmsg':'code is null'})


class GetAuthUserInfo(APIView):
    permission_classes = ()
    def get(self, request):
        openid = request.GET.get('openid')
        if not openid:
            return Response({'errcode':-3, 'errmsg':'openid is null'})
        w_user = WeixinUser.objects.filter(openid=openid).first()
        if not w_user:
            return Response({'errcode':-4, 'errmsg':'openid is not exist'})
        if w_user.nickname:

            return Response({
                       "openid":openid,
                       "nickname": w_user.nickname,
                       "sex": w_user.sex,
                       "province": w_user.province,
                       "city": w_user.city,
                       "country": w_user.country,
                        "headimgurl": w_user.headimgurl,
                        "unionid": w_user.unionid,
                    })
        if not w_user.auth_info:
            return Response({'errcode':-5, 'errmsg':'openid auth info is null'})
        # print w_user.account_original_id
        account = Account.objects.get(original_id=w_user.account_original_id)
        if not account:
            return Response({'errcode':-6, 'errmsg':u'公众号信息错误或者不存在'})
        try:
            oauth = WeChatOAuth(account.app_id, account.app_secret, )
            if not w_user.auth_info.check_access_token():
                res = oauth.refresh_access_token(w_user.auth_info.refresh_token)
                w_user.auth_info.access_token = res['access_token']
                w_user.auth_info.refresh_token = res['refresh_token']
                w_user.auth_info.access_token_expires_at = Account._now() + datetime.timedelta(seconds=res.get('expires_in') - 60)
                w_user.auth_info.save()
            user_info = oauth.get_user_info(w_user.openid, w_user.auth_info.access_token)
            w_user.nickname = user_info.get('nickname', "")
            w_user.sex = user_info.get('sex')
            w_user.city = user_info.get('city', "")
            w_user.country = user_info.get('country', "")
            w_user.headimgurl = user_info.get('headimgurl', "")
            w_user.unionid =  user_info.get('unionid', '')
            w_user.province = user_info.get('province', '')
            w_user.save()
            return Response(user_info)
        except WeChatException, e:
            return Response({'errcode':e.errcode, 'errmsg':e.errmsg})

class GetUserInfo(APIView):
    renderer_classes = (renderers.UnicodeJSONRenderer,)
    permission_classes = ()

    def get(self, request):
        openid = request.GET.get('openid')
        if not openid:
            return Response({'errcode':-3, 'errmsg':'openid is null'})
        w_user = WeixinUser.objects.filter(openid=openid).first()
        if not w_user:
            return Response({'errcode':-4, 'errmsg':'openid is not exist'})
        if w_user.nickname:
            return Response({
                       "openid":openid,
                       "nickname": w_user.nickname,
                       "sex": w_user.sex,
                       "province": w_user.province,
                       "city": w_user.city,
                       "country": w_user.country,
                        "headimgurl": w_user.headimgurl,
                        "unionid": w_user.unionid,
                        'subscribe': w_user.subscribe,
                        'subscribe_time': w_user.subscribe_time
                    })
        account = Account.objects.get(original_id=w_user.account_original_id)
        if not account:
            return Response({'errcode':-6, 'errmsg':u'公众号信息错误或者不存在'})
        try:
            user_info = account.get_user_info(w_user.openid)
            w_user.nickname = user_info.get('nickname', "")
            w_user.sex = user_info.get('sex')
            w_user.city = user_info.get('city', "")
            w_user.country = user_info.get('country', "")
            w_user.headimgurl = user_info.get('headimgurl', "")
            w_user.unionid =  user_info.get('unionid', '')
            w_user.province = user_info.get('province', '')
            w_user.subscribe = user_info.get('subscribe', '')
            w_user.subscribe_time = user_info.get('subscribe_time', '')
            w_user.save()
            return Response(user_info)
        except WeChatException, e:
            return Response({'errcode':e.errcode, 'errmsg':e.errmsg})




