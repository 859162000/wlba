# encoding:utf-8
from django.views.generic import View, TemplateView, RedirectView
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login, logout
from django.conf import settings
from django.shortcuts import redirect
from django.db.models.signals import post_save, pre_save
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import renderers
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
import json
import logging
import urllib
import base64

from .models import WeixinUser
from .views import JumpPageTemplate, redirectToJumpPage
from misc.models import Misc


logger = logging.getLogger("weixin")

class BaseWeixinTemplate(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        openid = self.request.GET.get('openid')
        if not openid:
            redirect_uri = settings.CALLBACK_HOST + reverse(self.url_name)
            count = 0
            for key in self.request.GET.keys():
                if count == 0:
                    redirect_uri += '?%s=%s'%(key, self.request.GET.get(key))
                else:
                    redirect_uri += "&%s=%s"%(key, self.request.GET.get(key))
                count += 1
            redirect_uri = urllib.quote(redirect_uri)
            account_id = 3
            key = 'share_redpack'
            shareconfig = Misc.objects.filter(key=key).first()
            if shareconfig:
                shareconfig = json.loads(shareconfig.value)
                if type(shareconfig) == dict:
                    account_id = shareconfig['account_id']
            redirect_url = reverse('weixin_authorize_code')+'?state=%s&redirect_uri=%s' % (account_id, redirect_uri)
            # print redirect_url
            return HttpResponseRedirect(redirect_url)
        w_user = WeixinUser.objects.filter(openid=openid).first()
        if not w_user:
            return redirectToJumpPage("error")
        if not w_user.user:
            return redirectToJumpPage(u"请先绑定网利宝账号")

        return super(BaseWeixinTemplate, self).dispatch(request, *args, **kwargs)



class AwardIndexTemplate(BaseWeixinTemplate):
    template_name = "sub_award.jade"

    def get_context_data(self, **kwargs):
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

        return {
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





