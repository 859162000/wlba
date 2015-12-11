# encoding:utf-8
from django.views.generic import View, TemplateView, RedirectView
from django.http import  HttpResponseRedirect

from django.core.urlresolvers import reverse
from wechatpy.oauth import WeChatOAuth

from django.conf import settings
import json
import logging
import urllib
import base64
from .models import WeixinUser, WeixinAccounts
from misc.models import Misc
from wanglibao_account.backends import invite_earning
from weixin.common.decorators import weixin_api_error

logger = logging.getLogger("weixin")
# https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx18689c393281241e&redirect_uri=http://2ea0ef54.ngrok.io/weixin/award_index/&response_type=code&scope=snsapi_base&state=1#wechat_redirect
class BaseWeixinTemplate(TemplateView):
    @weixin_api_error
    def dispatch(self, request, *args, **kwargs):
        code = request.GET.get('code')
        state = request.GET.get('state')
        error_msg = "code or state is None"
        if code and state:
            account = WeixinAccounts.getByOriginalId(state)
            request.session['account_key'] = account.key
            oauth = WeChatOAuth(account.app_id, account.app_secret, )
            res = oauth.fetch_access_token(code)
            openid = res.get('openid')
            w_user = WeixinUser.objects.filter(openid=openid).first()

            if not w_user:
                error_msg = "error"
            if not w_user.user:
                error_msg = u"请先绑定网利宝账号"
        if error_msg:
            from .views import redirectToJumpPage
            return redirectToJumpPage(error_msg)
        return super(BaseWeixinTemplate, self).dispatch(request, *args, **kwargs)



class AwardIndexTemplate(BaseWeixinTemplate):
    template_name = "sub_award.jade"

    def get_context_data(self, **kwargs):
        print self.request.__dict__
        openid = self.request.GET.get('openid')
        return {
            "openid": openid,
        }
    def dispatch(self, request, *args, **kwargs):
        self.url_name = 'award_index'
        return super(AwardIndexTemplate, self).dispatch(request, *args, **kwargs)


class InviteWeixinFriendTemplate(BaseWeixinTemplate):
    template_name = "sub_invite_server.jade"

    def get_context_data(self, **kwargs):
        openid = self.request.GET.get('openid')
        w_user = WeixinUser.objects.filter(openid=openid).first()
        user = w_user.user
        earning = 0
        if user:
            earning = invite_earning(user)

        return {
            "earning":earning,
            "callback_host":settings.CALLBACK_HOST,
            "url": base64.b64encode(w_user.user.wanglibaouserprofile.phone),
        }
    def dispatch(self, request, *args, **kwargs):
        self.url_name = 'sub_invite'
        return super(InviteWeixinFriendTemplate, self).dispatch(request, *args, **kwargs)


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





