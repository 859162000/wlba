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
import functools
import re

from wanglibao_account.forms import EmailOrPhoneAuthenticationForm
from wanglibao_account.forms import LoginAuthenticationNoCaptchaForm
from wanglibao_buy.models import FundHoldInfo
from wanglibao_banner.models import Banner
from wanglibao_p2p.models import P2PEquity, P2PProduct
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_redpack import backends
from wanglibao_rest import utils
from django.contrib.auth.models import User
from constant import MessageTemplate
from constant import (ACCOUNT_INFO_TEMPLATE_ID, BIND_SUCCESS_TEMPLATE_ID, UNBIND_SUCCESS_TEMPLATE_ID,
                      PRODUCT_ONLINE_TEMPLATE_ID, AWARD_COUPON_TEMPLATE_ID)
from weixin.util import getAccountInfo
from wanglibao_profile.models import WanglibaoUserProfile
import weixin.tasks

from wanglibao_pay.models import Bank
from wechatpy import parse_message, create_reply, WeChatClient
from wechatpy.replies import TransferCustomerServiceReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException, WeChatException
from wechatpy.oauth import WeChatOAuth
from weixin.common.decorators import weixin_api_error
from weixin.common.wx import generate_js_wxpay
from .models import Account, WeixinUser, WeixinAccounts, AuthorizeInfo, QrCode, SubscribeService, SubscribeRecord, WeiXinChannel
# from .common.wechat import tuling
from decimal import Decimal
from wanglibao_pay.models import Card
from marketing.utils import get_channel_record
import json
import uuid
import urllib
import logging
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from wanglibao_p2p.views import get_p2p_list
from wanglibao_redis.backend import redis_backend
from rest_framework import renderers
from misc.models import Misc
from wechatpy.parser import parse_message
from wechatpy.messages import BaseMessage, TextMessage
import datetime, time
from .util import _generate_ajax_template
from wechatpy.events import (BaseEvent, ClickEvent, SubscribeScanEvent, ScanEvent, UnsubscribeEvent, SubscribeEvent,\
                             TemplateSendJobFinishEvent)
from .views import getOrCreateWeixinUser, WeixinJoinView

logger = logging.getLogger("weixin")

class SubWeixinJoinView(WeixinJoinView):
    account = None

    def post(self, request, account_key):
        logger.debug("entering post=============================/weixin/join/%s"%account_key)
        if not self.check_signature(request, account_key):
            return HttpResponseForbidden()
        # account = Account.objects.get(pk=account_key) #WeixinAccounts.get(account_key)
        self.msg = parse_message(request.body)
        logger.debug(self.msg)
        msg = self.msg
        reply = None
        toUserName = msg._data['ToUserName']
        fromUserName = msg._data['FromUserName']
        createTime = msg._data['CreateTime']
        weixin_account = WeixinAccounts.getByOriginalId(toUserName)
        if isinstance(msg, BaseEvent):
            if isinstance(msg, ClickEvent):
                reply = self.process_click_event(msg)
            elif isinstance(msg, SubscribeEvent):
                reply = self.process_subscribe(msg, toUserName)
            elif isinstance(msg, UnsubscribeEvent):
                w_user = getOrCreateWeixinUser(fromUserName, weixin_account)
                if w_user.subscribe != 0:
                    w_user.subscribe = 0
                w_user.unsubscribe_time = int(time.time())
                w_user.user = None
                w_user.save()
                reply = create_reply(u'欢迎下次关注我们！', msg)
            elif isinstance(msg, SubscribeScanEvent):
                reply = self.process_subscribe(msg, toUserName)
            elif isinstance(msg, ScanEvent):
                #如果eventkey为用户id则进行绑定
                reply = self.process_subscribe(msg, toUserName)
            elif isinstance(msg, TemplateSendJobFinishEvent):
                reply = -1
        elif isinstance(msg, BaseMessage):
            if isinstance(msg, TextMessage):
                reply = self.check_service_subscribe(msg, weixin_account)
                if not reply:
                    # 多客服转接
                    reply = TransferCustomerServiceReply(message=msg)
        if reply == -1 or not reply:
            return HttpResponse("")
        return HttpResponse(reply.render())

    def process_click_event(self, msg):
        return -1

    def process_subscribe(self, msg, toUserName):
        replay = super(SubWeixinJoinView, self).process_subscribe(msg, toUserName)
        return replay

    def check_service_subscribe(self, msg, weixin_account):
        return -1