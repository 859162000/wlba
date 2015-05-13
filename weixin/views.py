# encoding:utf-8
from django.views.generic import View, TemplateView, RedirectView
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from weixin.wechatpy import WeChatClient, parse_message, create_reply
from weixin.wechatpy.replies import TransferCustomerServiceReply
from weixin.wechatpy.utils import check_signature
from weixin.wechatpy.exceptions import InvalidSignatureException
from weixin.wechatpy.oauth import WeChatOAuth
from .models import Account, WeixinUser
from .common.wechat import tuling
from wanglibao_buy.models import FundHoldInfo
from wanglibao_p2p.models import P2PProduct, P2PEquity
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_p2p.serializers import P2PProductSerializer
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from django.template import Template, Context
from django.template.loader import render_to_string, get_template
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from django.db.models import Q
from rest_framework.authtoken.views import ObtainAuthToken
from wanglibao_rest.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
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

        if msg.type == 'text':
            if msg.content == 'Dkf':
                reply = TransferCustomerServiceReply(message=msg)
            else:
                reply = tuling(msg)
        else:
            reply = create_reply(u'更多功能，敬请期待！', msg)

        return HttpResponse(reply.render())

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ConnectView, self).dispatch(request, *args, **kwargs)


class WeixinJsapiConfig(View):

    def get(self, request, id):
        try:
            account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            data = {'errcode': 1, 'errmsg': 'account does not exist'}
            return HttpResponse(json.dumps(data), 'application/json')

        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        noncestr = uuid.uuid1().hex
        timestamp = str(int(time.time()))
        url = request.META.get('HTTP_REFERER')
        signature = client.jsapi.get_jsapi_signature(noncestr, account.jsapi_ticket, timestamp, url)
        data = {
            'app_id': account.app_id,
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'signature': signature
        }
        return HttpResponse(json.dumps(data), 'application/json')


class WeixinLogin(TemplateView):
    template_name = 'test_login.html'

    def get_context_data(self, **kwargs):
        context = super(WeixinLogin, self).get_context_data(**kwargs)
        code = self.request.GET.get('code')

        if code:
            account_id = self.request.GET.get('state')
            try:
                account = Account.objects.get(pk=account_id)
            except Account.DoesNotExist:
                return HttpResponseNotFound()

            oauth = WeChatOAuth(account.app_id, account.app_secret)
            res = oauth.fetch_access_token(code)
            if not res.get('errcode'):
                account.oauth_access_token = res.get('access_token')
                account.oauth_access_token_expires_in = res.get('expires_in')
                account.oauth_refresh_token = res.get('refresh_token')
                account.save()
                WeixinUser.objects.get_or_create(openid=res.get('openid'))
                context['openid'] = res.get('openid')

        return context


class ObtainAuthTokenCustomized(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA)
        # 设备类型，默认为IOS
        device_type = request.DATA.get('device_type', 'ios')

        if serializer.is_valid():
            try:
                openid = request.DATA.get('openid')
                weixin_user = WeixinUser.objects.get(openid=openid)
                weixin_user.user = serializer.object['user']
                weixin_user.save()
            except WeixinUser.DoesNotExist:
                pass

            if device_type not in ('ios', 'android'):
                return Response({'message': 'device_type error'}, status=status.HTTP_200_OK)

            token, created = Token.objects.get_or_create(user=serializer.object['user'])
            return Response({'token': token.key, 'user_id': serializer.object['user'].id}, status=status.HTTP_200_OK)

        if device_type == 'ios':
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'token': 'false'}, status=status.HTTP_200_OK)


class WeixinOauthLoginRedirect(RedirectView):

    def get_redirect_url(self, id, *args, **kwargs):
        try:
            account = Account.objects.get(pk=id)
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

        return {
            'p2p_lists': p2p_lists
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
        }

