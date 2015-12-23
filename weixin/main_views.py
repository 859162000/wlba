# encoding:utf-8
from django.views.generic import TemplateView
import urllib
from django.contrib.auth import login as auth_login
from wechatpy.oauth import WeChatOAuth
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from decimal import Decimal
from django.http import HttpResponseRedirect, Http404
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.conf import settings

from weixin.common.decorators import weixin_api_error
from weixin.models import WeixinAccounts, WeixinUser
from weixin.util import redirectToJumpPage, bindUser, unbindUser
from marketing.utils import get_channel_record
from util import getAccountInfo, get_fwh_login_url
from wanglibao_account.forms import LoginAuthenticationNoCaptchaForm
from wanglibao.templatetags.formatters import safe_phone_str
from .forms import OpenidAuthenticationForm
from wanglibao_p2p.common import get_p2p_list
from wanglibao_redis.backend import redis_backend
from wanglibao_rest import utils
from wanglibao_redpack import backends
from .util import _generate_ajax_template
logger = logging.getLogger("weixin")


class WXLoginRedirect(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        next = request.GET.get('next')
        login_url = get_fwh_login_url(next=next)
        print '---------', login_url
        return HttpResponseRedirect(login_url)


class WXLogin(TemplateView):
    template_name = 'weixin_login_new.jade'

    def get_context_data(self, *args, **kwargs):
        context = super(WXLogin, self).get_context_data(**kwargs)
        self.request.session['openid'] = self.openid
        next = self.request.GET.get('next', '')
        next = urllib.unquote(next.encode('utf-8'))

        return {
            'context': context,
            'next': next,
            }

    @weixin_api_error
    def dispatch(self, request, *args, **kwargs):
        code = request.GET.get('code')
        state = request.GET.get('state')
        error_msg = ""
        if code and state:
            account = WeixinAccounts.getByOriginalId(state)
            request.session['account_key'] = account.key
            oauth = WeChatOAuth(account.app_id, account.app_secret, )
            res = oauth.fetch_access_token(code)
            self.openid = res.get('openid')
            form = OpenidAuthenticationForm(self.openid, data=request.GET)
            if form.is_valid():
                auth_login(request, form.get_user())
                next = self.request.GET.get('next', '')
                next = urllib.unquote(next.encode('utf-8'))
                return redirectToJumpPage("自动登录成功", next=next)
            else:
                return super(WXLogin, self).dispatch(request, *args, **kwargs)
        else:
            error_msg = u"code or state is None"
        if error_msg:
            return redirectToJumpPage(error_msg)

class WXLoginAPI(APIView):
    permission_classes = ()
    http_method_names = ['post']

    def _form(self, request):
        return LoginAuthenticationNoCaptchaForm(request, data=request.POST)

    def post(self, request):
        form = self._form(request)

        if form.is_valid():
            user = form.get_user()
            try:
                openid = request.session.get('openid')
                if openid:
                    weixin_user = WeixinUser.objects.get(openid=openid)
                    rs, txt = bindUser(weixin_user, user)
                    if rs == 0:
                        auth_login(request, user)
                        request.session.set_expiry(1800)
            except WeixinUser.DoesNotExist:
                pass
            data = {'nickname': user.wanglibaouserprofile.nick_name}
            return Response(data)

        return Response(form.errors, status=400)


class WXRegister(TemplateView):
    template_name = 'weixin_regist_new.jade'

    def get_context_data(self, **kwargs):
        token = self.request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, '')
        token_session = self.request.session.get(settings.PROMO_TOKEN_QUERY_STRING, '')
        if token:
            token = token
        elif token_session:
            token = token_session
        else:
            token = 'fwh'

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
            'next': next,
        }

class AccountTemplate(TemplateView):

    def get_context_data(self, **kwargs):
        account_info = getAccountInfo(self.request.user)
        print account_info
        return {
            'total_asset': account_info['total_asset'],
            'total_unpaid_interest': account_info['p2p_total_unpaid_interest'],
            'total_paid_interest': account_info['p2p_total_paid_interest'],
            'margin': account_info['p2p_margin'],
        }

class RechargeTemplate(TemplateView):
    def get_context_data(self, **kwargs):
        margin = self.request.user.margin.margin
        return {
            'margin': margin if margin else 0.0
        }


class FwhP2PlistTemplate(TemplateView):
    def get_context_data(self, **kwargs):
        p2p_products = []
        p2p_done_list, p2p_full_list, p2p_repayment_list, p2p_finished_list = get_p2p_list()
        p2p_products.extend(p2p_done_list)
        p2p_products.extend(p2p_full_list)
        p2p_products.extend(p2p_repayment_list)
        p2p_products.extend(p2p_finished_list)
        print '############################', p2p_products
        limit = 10
        paginator = Paginator(p2p_products, limit)
        page = self.request.GET.get('page')

        try:
            p2p_products = paginator.page(page)
        except PageNotAnInteger:
            p2p_products = paginator.page(1)
        except EmptyPage:
            p2p_products = []
        except Exception:
            p2p_products = paginator.page(paginator.num_pages)

        phone = self.request.user.wanglibaouserprofile.phone
        margin = self.request.user.margin.margin

        return {
            'results': p2p_products[:10],
            'phone': safe_phone_str(phone),
            'margin': margin
        }

class FWHP2PDetail(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(FWHP2PDetail, self).get_context_data(**kwargs)

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

        user = self.request.user

        device = utils.split_ua(self.request)
        result = backends.list_redpack(user, 'available', device['device_type'], p2p['id'])
        redpacks = result['packages'].get('available', [])
        context.update({
            "p2p":p2p,
            "redpacks":redpacks,
        })
        return context


class P2PListFWH(APIView):
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

        html_data = _generate_ajax_template(p2p_products, 'include/ajax/service_ajax_list.jade')

        return Response({
            'html_data': html_data,
            'page': page,
            'pagesize': pagesize,
        })





