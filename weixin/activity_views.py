# encoding:utf-8
from django.views.generic import TemplateView
from django.conf import settings
import json
import logging
import base64
from .models import WeixinUser
from wanglibao_account.backends import invite_earning
from .base import BaseWeixinTemplate

logger = logging.getLogger("weixin")
# https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx18689c393281241e&redirect_uri=http://2ea0ef54.ngrok.io/weixin/award_index/&response_type=code&scope=snsapi_base&state=1#wechat_redirect

class InviteWeixinFriendTemplate(TemplateView):
    template_name = "sub_invite_server.jade"

    def get_context_data(self, **kwargs):
        user = self.request.user
        earning = 0
        if user:
            earning = invite_earning(user)

        return {
            "earning":earning,
            "callback_host":settings.CALLBACK_HOST,
            "url": base64.b64encode(user.wanglibaouserprofile.phone),
        }
    def dispatch(self, request, *args, **kwargs):
        self.url_name = 'sub_invite'
        return super(InviteWeixinFriendTemplate, self).dispatch(request, *args, **kwargs)







