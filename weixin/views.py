# encoding:utf-8
from django.views.generic import View, TemplateView, RedirectView
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login
from django.template import Template, Context
from django.template.loader import get_template
from django.db.models import Q
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
from weixin.wechatpy import WeChatClient, parse_message, create_reply
from weixin.wechatpy.replies import TransferCustomerServiceReply
from weixin.wechatpy.utils import check_signature
from weixin.wechatpy.exceptions import InvalidSignatureException
from weixin.wechatpy.oauth import WeChatOAuth
from weixin.common.decorators import weixin_api_error
from .models import Account, WeixinUser
from .common.wechat import tuling
from decimal import Decimal
import datetime
import json
import time
import uuid

# Create your views here.


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
        url = request.META.get('HTTP_REFERER')
        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        signature = client.jsapi.get_jsapi_signature(noncestr, account.jsapi_ticket, timestamp, url)

        data = {
            'appId': account.app_id,
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
            except WeChatClient, e:
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
    template_name = 'weixin_detail.jade'

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

        current_equity = 0
        user = self.request.user
        if user.is_authenticated():
            equity_record = p2p.equities.filter(user=user).first()
            if equity_record is not None:
                current_equity = equity_record.equity

        orderable_amount = min(p2p.limit_amount_per_user - current_equity, p2p.remain)
        total_buy_user = P2PEquity.objects.filter(product=p2p).count()


        context.update({
            'p2p': p2p,
            'end_time': end_time,
            'orderable_amount': orderable_amount,
            'total_earning': total_earning,
            'current_equity': current_equity,
            'attachments': p2p.attachment_set.all(),
            'total_fee_earning': total_fee_earning,
            'total_buy_user': total_buy_user,
        })

        return context


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


class P2PDetailBuyView(TemplateView):
    template_name = 'weixin_buy.jade'

    def get_context_data(self, id, **kwargs):
        context = super(P2PDetailBuyView, self).get_context_data(**kwargs)

        try:
            p2p = P2PProduct.objects.exclude(status=u'流标').exclude(status=u'录标').get(pk=id, hide=False)

            if p2p.soldout_time:
                end_time = p2p.soldout_time
            else:
                end_time = p2p.end_time
        except P2PProduct.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        amount = self.request.GET.get('amount', 0)

        user = self.request.user
        user_margin = user.margin.margin

        terms = get_amortization_plan(p2p.pay_method).generate(p2p.total_amount,
                                                               p2p.expected_earning_rate / 100,
                                                               datetime.datetime.now(),
                                                               p2p.period)
        total_earning = terms.get('total') - p2p.total_amount
        total_fee_earning = 0

        if p2p.activity:
            total_fee_earning = Decimal(p2p.total_amount * p2p.activity.rule.rule_amount *
                                        (Decimal(p2p.period) / Decimal(12))).quantize(Decimal('0.01'))

        current_equity = 0
        equity_record = p2p.equities.filter(user=user).first()
        if equity_record is not None:
            current_equity = equity_record.equity

        orderable_amount = min(p2p.limit_amount_per_user - current_equity, p2p.remain)

        device = utils.split_ua(self.request)
        redpack = backends.list_redpack(user, 'available', device['device_type'])

        context.update({
            'p2p': p2p,
            'end_time': end_time,
            'user_margin': float(user_margin),
            'amount': float(amount),
            'redpack': redpack,
            'current_equity': current_equity,
            'orderable_amount': orderable_amount,
            'total_earning': total_earning,
            'total_fee_earning': total_fee_earning,
        })

        return context


class CalculatorView(TemplateView):
    template_name = 'weixin_calculator.jade'

    def get_context_data(self, id, **kwargs):
        context = super(CalculatorView, self).get_context_data(**kwargs)

        try:
            p2p = P2PProduct.objects.exclude(status=u'流标').exclude(status=u'录标').get(pk=id, hide=False)

            if p2p.soldout_time:
                end_time = p2p.soldout_time
            else:
                end_time = p2p.end_time
        except P2PProduct.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        user_margin = 0
        user = self.request.user
        if user.is_authenticated():
            user_margin = user.margin.margin

        terms = get_amortization_plan(p2p.pay_method).generate(p2p.total_amount,
                                                               p2p.expected_earning_rate / 100,
                                                               datetime.datetime.now(),
                                                               p2p.period)
        total_earning = terms.get('total') - p2p.total_amount
        total_fee_earning = 0

        if p2p.activity:
            total_fee_earning = Decimal(p2p.total_amount * p2p.activity.rule.rule_amount *
                                        (Decimal(p2p.period) / Decimal(12))).quantize(Decimal('0.01'))

        current_equity = 0
        if user.is_authenticated():
            equity_record = p2p.equities.filter(user=user).first()
            if equity_record is not None:
                current_equity = equity_record.equity

        orderable_amount = min(p2p.limit_amount_per_user - current_equity, p2p.remain)

        context.update({
            'p2p': p2p,
            'end_time': end_time,
            'margin': float(user_margin),
            'orderable_amount': orderable_amount,
            'total_earning': total_earning,
            'total_fee_earning': total_fee_earning,
        })

        return context
