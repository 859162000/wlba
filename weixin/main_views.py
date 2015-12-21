# encoding:utf-8
from django.views.generic import TemplateView
import urllib
from django.contrib.auth import login as auth_login
from wechatpy.oauth import WeChatOAuth
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
import json
from django.core.urlresolvers import reverse

from weixin.common.decorators import weixin_api_error
from weixin.models import WeixinAccounts, WeixinUser
from weixin.util import redirectToJumpPage, bindUser, unbindUser
from marketing.utils import get_channel_record
from util import getOrCreateWeixinUser
from wanglibao_account.forms import LoginAuthenticationNoCaptchaForm
from wanglibao import settings
from wanglibao_account.views import ajax_register
from misc.models import Misc
from .forms import OpenidAuthenticationForm
from django.conf import settings

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
                return redirectToJumpPage("自动登录成功")
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
            token = 'weixin'

        if token:
            channel = get_channel_record(token)
        else:
            channel = None
        phone = self.request.GET.get('phone', 0)
        next = self.request.GET.get('next', '')
        print '-----------------------------', self.request.session.get('openid')
        return {
            'token': token,
            'channel': channel,
            'phone': phone,
            'next': next,
        }

    @weixin_api_error
    def dispatch(self, request, *args, **kwargs):
        self.openid = self.request.session.get('openid', "")
        if self.openid:
            form = OpenidAuthenticationForm(self.openid, data=request.GET)
            if form.is_valid():
                auth_login(request, form.get_user())
                return redirectToJumpPage("自动登录成功")
            else:
                return super(WXRegister, self).dispatch(request, *args, **kwargs)
        else:
            super(WXRegister, self).dispatch(request, *args, **kwargs)

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache

@sensitive_post_parameters()
@csrf_protect
@never_cache
def ajax_wx_register(request):
    openid = request.session.get('openid')
    response = ajax_register(request)
    if response.status_code==200 and openid:
        w_user = WeixinUser.objects.get(openid=openid)
        bindUser(w_user, request.user)
    return response

# class WXRegisterAPI(APIView):
#     permission_classes = ()
#     http_method_names = ['post']
#
#     def post(self, request):
#         openid = self.request.session.get('openid')
#         response = ajax_register(request)
#         if response.status_code==200 and openid:
#             w_user = WeixinUser.objects.get(openid=openid)
#             bindUser(w_user, request.user)
#         return response

