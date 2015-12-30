# encoding:utf-8
from django.views.generic import TemplateView
from wechatpy.oauth import WeChatOAuth

from util import redirectToJumpPage
from weixin.models import WeixinUser, WeixinAccounts
from weixin.common.decorators import weixin_api_error
from misc.models import Misc
import json
from rest_framework.views import APIView
from wanglibao import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
import requests

class OpenIdBaseAPIView(APIView):
    @weixin_api_error
    def initial(self, request, *args, **kwargs):
        code = request.GET.get('code')
        state = request.GET.get('state')
        self.openid = ""
        if code and state:
            account = WeixinAccounts.getByOriginalId(state)
            request.session['account_key'] = account.account_key
            oauth = WeChatOAuth(account.app_id, account.app_secret, )
            res = oauth.fetch_access_token(code)
            self.openid = res.get('openid')

class BaseWeixinTemplate(TemplateView):
    @weixin_api_error
    def dispatch(self, request, *args, **kwargs):
        code = request.GET.get('code')
        state = request.GET.get('state')
        error_msg = ""
        if code and state:
            account = WeixinAccounts.getByOriginalId(state)
            request.session['account_key'] = account.account_key
            oauth = WeChatOAuth(account.app_id, account.app_secret, )
            res = oauth.fetch_access_token(code)
            self.openid = res.get('openid')
            w_user = WeixinUser.objects.filter(openid=self.openid).first()
            if not w_user:
                error_msg = "error"
            if not w_user.user:
                error_msg = u"请先绑定网利宝账号"
        else:
            error_msg = u"code or state is None"
        if error_msg:

            return redirectToJumpPage(error_msg)
        return super(BaseWeixinTemplate, self).dispatch(request, *args, **kwargs)

class ChannelBaseTemplate(TemplateView):
    wx_classify = ''
    wx_code = ''

    def get_context_data(self, **kwargs):
        # print '---------------------------%s'%self.wx_classify
        context = super(ChannelBaseTemplate, self).get_context_data(**kwargs)
        m = Misc.objects.filter(key='weixin_qrcode_info').first()
        if m and m.value:
            info = json.loads(m.value)
            if info.get(self.wx_classify):
                context['original_id'] = info.get(self.wx_classify)
        context['code'] = self.wx_code
        return context

class LowBaseWeixinTemplate(TemplateView):
    openid = ''
    nick_name = ''
    head_img = ''
    url_name = ''
    wx_classify = 'fwh'

    def getAccountid(self):
        m = Misc.objects.filter(key='weixin_qrcode_info').first()
        if m and m.value:
            info = json.loads(m.value)
            if info.get(self.wx_classify):
                return info.get(self.wx_classify)

    def getOpenid(self, request, *args, **kwargs):
        account_id = self.getAccountid()
        redirect_uri = settings.CALLBACK_HOST + reverse(self.url_name)
        self.openid = self.request.session.get('WECHAT_OPEN_ID', None)
        if not self.openid:
            self.openid = self.request.GET.get('openid', None)
            if self.openid:
                self.request.session['WECHAT_OPEN_ID'] = self.openid
            else:
                redirect_url = reverse('weixin_authorize_code')+'?state=%s&redirect_uri=%s' % (account_id, redirect_uri)
                return HttpResponseRedirect(redirect_url)

        w_user = WeixinUser.objects.filter(openid=self.openid).first()
        if not w_user:
            #TODO:
            pass

        if not w_user.nickname or not w_user.headimgurl :
            res = requests.request(
                method='get',
                url=settings.CALLBACK_HOST + reverse('weixin_get_user_info')+'?openid=%s'%self.openid,
            )
            result = res.json()
            if result.get('errcode'):
                redirect_url = reverse('weixin_authorize_code')+'?state=%s&auth=1&redirect_uri=%s' % (account_id, redirect_uri)
                return HttpResponseRedirect(redirect_url)
            else:
                self.nick_name = result.get('nickname')
                self.head_img = result.get('headimgurl')

        #return super(LowBaseWeixinTemplate, self).dispatch(request, *args, **kwargs)

