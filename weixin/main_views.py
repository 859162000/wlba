# encoding:utf-8
from django.views.generic import TemplateView
import urllib
from django.contrib.auth import login as auth_login
from wechatpy.oauth import WeChatOAuth
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse

from weixin.common.decorators import weixin_api_error
from weixin.models import WeixinAccounts, WeixinUser
from weixin.util import redirectToJumpPage, bindUser, unbindUser
from marketing.utils import get_channel_record
from util import getOrCreateWeixinUser
from wanglibao_account.forms import LoginAuthenticationNoCaptchaForm
from wanglibao import settings
from wanglibao_account.views import ajax_register



class WXLogin(TemplateView):
    template_name = 'weixin_login_new.jade'

    def get_context_data(self, request, *args, **kwargs):
        context = super(WXLogin, self).get_context_data(**kwargs)
        context['openid'] = self.openid
        next = request.GET.get('next', '')
        next = urllib.unquote(next.encode('utf-8'))
        return {
            'context': context,
            'next': next
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
            w_user, old_subscribe = getOrCreateWeixinUser(self.openid, account)
            user = w_user.user
            if user:
                auth_login(request, user)
        else:
            error_msg = u"code or state is None"
        if error_msg:
            return redirectToJumpPage(error_msg)
        return super(WXLogin, self).dispatch(request, *args, **kwargs)

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
                openid = request.POST.get('openid')
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
        openid = self.request.GET.get('openid', '')
        return {
            'token': token,
            'channel': channel,
            'phone': phone,
            'openid':openid,
            'next': next
        }

class WXRegisterAPI(APIView):
    permission_classes = ()
    http_method_names = ['post']

    def post(self, request):
        openid = request.DATA.get('openid')
        if openid:
            w_user = WeixinUser.objects.get(openid=openid)
            response = ajax_register(request)
            if response.status_code==200:
                bindUser(w_user, request.user)
            return response
        else:
            return HttpResponse({"error_code":-1, 'message':"openid is null"})

