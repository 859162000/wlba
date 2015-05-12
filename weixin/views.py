# encoding:utf-8
from django.shortcuts import render_to_response
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

        # reply = create_reply(u'更多功能，敬请期待！', msg)
        if msg.type == 'text':
            if msg.content in ['dkf', 'DKF', 'Dkf' u'多客服']:
                reply = TransferCustomerServiceReply()
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
            return HttpResponse(json.dumps({'errcode': 1, 'errmsg': 'account does not exist'}), 'application/json')
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


class WeixinLogin(View):

    def get(self, request):
        code = request.GET.get('code')
        if code:
            account_id = request.GET.get('state')
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
                request.session['openid'] = res.get('openid')

        return render_to_response('login.html')

    def post(self, request):
        from django.contrib.auth import authenticate, login
        user = authenticate(identifier=request.POST.get('identifier'), password=request.POST.get('password'))
        if user:
            if not user.is_active:
                data = {'errcode': 1, 'errmsg': 'User account is disabled.'}
                return HttpResponse(json.dumps(data), 'application/json')

            if user.wanglibaouserprofile.frozen:
                data = {'errcode': 1, 'errmsg': 'User account is frozen.'}
                return HttpResponse(json.dumps(data), 'application/json')

            try:
                weixin_user = WeixinUser.objects.get(openid=request.session.get('openid'))
                weixin_user.user = user
                weixin_user.save()
            except WeixinUser.DoesNotExist:
                pass

            login(request, user)
            data = {'errcode': 0}
            return HttpResponse(json.dumps(data), 'application/json')

        data = {'errcode': 1, 'errmsg': 'login failed'}
        return HttpResponse(json.dumps(data), 'application/json')


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

        maxid = request.GET.get('maxid', '')
        minid = request.GET.get('minid', '')

        pager = None
        if maxid and not minid:
            pager = Q(id__gt=maxid)
        if minid and not maxid:
            pager = Q(id__lt=minid)

        if pager:
            p2p_lists = P2PProduct.objects.filter(hide=False).filter(status__in=[
                u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
            ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).filter(pager).order_by('-priority', '-publish_time')[:10]
        else:
            p2p_lists = P2PProduct.objects.filter(hide=False).filter(status__in=[
                u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
            ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).order_by('-priority', '-publish_time')[:10]

        html_data = _generate_ajax_template(p2p_lists, 'include/ajax/ajax_list.jade')

        return Response({
            'html_data': html_data,
        })


class P2PDetailView(TemplateView):
    template_name = "weixin_detail.jade"

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
        total_earning = terms.get("total") - p2p.total_amount
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

