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
from django.db.models import Q
from wechatpy.exceptions import WeChatException
from weixin.common.decorators import is_check_id_verify
from weixin.models import WeixinAccounts, WeixinUser
from weixin.util import redirectToJumpPage, bindUser, unbindUser
from marketing.utils import get_channel_record
from util import getAccountInfo, get_fwh_login_url
from wanglibao_account.forms import LoginAuthenticationNoCaptchaForm
from wanglibao.templatetags.formatters import safe_phone_str
from .forms import OpenidAuthenticationForm
from wanglibao_p2p.common import get_p2p_list
from .util import _generate_ajax_template, FWH_LOGIN_URL, getOrCreateWeixinUser, getMiscValue
from wanglibao_pay.models import Bank, PayInfo, Card
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_redpack.backends import list_redpack
from experience_gold.backends import SendExperienceGold

logger = logging.getLogger("weixin")


class WXLoginRedirect(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        next = request.GET.get('next')
        login_url = get_fwh_login_url(next=next)
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

    def dispatch(self, request, *args, **kwargs):
        self.openid = self.request.session.get('openid')
        error_msg = ""
        if not self.openid:
            code = request.GET.get('code')
            state = request.GET.get('state')
            if code and state:
                try:
                    account = WeixinAccounts.getByOriginalId(state)
                    request.session['account_key'] = account.key
                    oauth = WeChatOAuth(account.app_id, account.app_secret, )
                    user_info = oauth.fetch_access_token(code)
                    self.openid = user_info.get('openid')
                    w_user, old_subscribe = getOrCreateWeixinUser(self.openid, account)
                    # w_user, is_first = WeixinUser.objects.get_or_create(openid=self.openid)
                    # if is_first:
                    #     w_user.save()
                except WeChatException, e:
                    error_msg = e.message
            else:
                error_msg = u"code or state is None"
            if error_msg:
                return redirectToJumpPage(error_msg)
        form = OpenidAuthenticationForm(self.openid, data=request.GET)
        if form.is_valid():
            auth_login(request, form.get_user())
            next = self.request.GET.get('next', '')
            next = urllib.unquote(next.encode('utf-8'))
            return redirectToJumpPage("自动登录成功", next=next)
        else:
            return super(WXLogin, self).dispatch(request, *args, **kwargs)



class WXLoginAPI(APIView):
    permission_classes = ()
    http_method_names = ['post']

    def _form(self, request):
        return LoginAuthenticationNoCaptchaForm(request, data=request.POST)

    def post(self, request):
        form = self._form(request)
        data = {}

        # add by ChenWeiBin@20160113
        phone = request.POST.get('identifier', '')
        profile = WanglibaoUserProfile.objects.filter(phone=phone, utype='3').first()
        if profile:
            return Response({'re_code': -1,
                             'errmessage': u'企业用户请在PC端登录'
                             }, status=400)

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
                        data = {'re_code':0,'nickname': user.wanglibaouserprofile.nick_name}
                    else:
                        data = {'re_code':rs, 'errmessage':txt}
            except WeixinUser.DoesNotExist, e:
                data = {'re_code':-1, 'errmessage':'wx_user does not exist'}
                logger.debug(e.message)

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
            'login_url': FWH_LOGIN_URL,
        }

class AccountTemplate(TemplateView):
    def get_context_data(self, **kwargs):
        account_info = getAccountInfo(self.request.user)
        info = getMiscValue("fwh_cfg_info")
        fetch_experience_url = info.get('fetch_experience_url', "").strip()
        fetch_coupon_url = info.get("fetch_coupon_url", "").strip()
        if not fetch_coupon_url.startswith("http"):
            if not fetch_coupon_url.startswith("/"):
                fetch_coupon_url=settings.CALLBACK_HOST + "/" + fetch_coupon_url
            else:
                fetch_coupon_url=settings.CALLBACK_HOST + fetch_coupon_url
        if not fetch_experience_url.startswith("http"):
            if not fetch_experience_url.startswith("/"):
                fetch_experience_url=settings.CALLBACK_HOST + "/" + fetch_experience_url
            else:
                fetch_experience_url=settings.CALLBACK_HOST + fetch_experience_url
        result = list_redpack(self.request.user, 'all', 'all', 0, 'all')
        seg = SendExperienceGold(self.request.user)
        experience_amount = seg.get_amount()
        print '=======================',{
            'total_asset': account_info['total_asset'],
            'total_unpaid_interest': account_info['p2p_total_unpaid_interest'],
            'total_paid_interest': account_info['p2p_total_paid_interest'],
            'margin': account_info['p2p_margin'],
            'fetch_experience_url':fetch_experience_url,
            'fetch_coupon_url':fetch_coupon_url,
            'coupon_num':len(result["packages"]['unused']),
            'experience_amount':experience_amount
        }

        return {
            'total_asset': account_info['total_asset'],
            'total_unpaid_interest': account_info['p2p_total_unpaid_interest'],
            'total_paid_interest': account_info['p2p_total_paid_interest'],
            'margin': account_info['p2p_margin'],
            'fetch_experience_url':fetch_experience_url,
            'fetch_coupon_url':fetch_coupon_url,
            'coupon_num':len(result["packages"]['unused']),
            'experience_amount':experience_amount
        }

class RechargeTemplate(TemplateView):
    def get_context_data(self, **kwargs):
        banks = Bank.get_kuai_deposit_banks()
        next = self.request.GET.get('rechargeNext', '')
        user = self.request.user
        pay_info = PayInfo.objects.filter(user=user)

        if pay_info.filter(status="成功"):
            recharge = True
        else:
            recharge = False
        margin = self.request.user.margin.margin
        return {
            'recharge': recharge,
            'banks': banks,
            'next' : next,
            'margin': margin if margin else 0.0,
        }

    @is_check_id_verify(True)
    def dispatch(self, request, *args, **kwargs):
        return super(RechargeTemplate, self).dispatch(request, *args, **kwargs)



class FwhP2PlistTemplate(TemplateView):
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
        except EmptyPage:
            p2p_products = []
        except Exception:
            p2p_products = paginator.page(paginator.num_pages)

        html_data = _generate_ajax_template(p2p_products, 'include/ajax/service_ajax_list.jade')

        return Response({
            'html_data': html_data,
            'page': page,
            'pagesize': pagesize,
        })


class FWHIdValidate(TemplateView):
    def get_context_data(self, **kwargs):

        return {

        }

    def dispatch(self, request, *args, **kwargs):
        return super(FWHIdValidate, self).dispatch(request, *args, **kwargs)
