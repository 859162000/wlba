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
from django.utils import timezone
from django.db.models import Q
import functools
import re
import random

from wanglibao_account.forms import LoginAuthenticationNoCaptchaForm
from wanglibao_buy.models import FundHoldInfo
from wanglibao_banner.models import Banner
from wanglibao_margin.php_utils import get_php_redis_principle, get_php_index_data
from wanglibao_p2p.models import P2PEquity, P2PProduct
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_pay.third_pay import card_bind_list
from wanglibao_redpack import backends
from wanglibao_rest import utils
from django.contrib.auth.models import User
from constant import MessageTemplate
from constant import (ACCOUNT_INFO_TEMPLATE_ID, UNBIND_SUCCESS_TEMPLATE_ID,
                      PRODUCT_ONLINE_TEMPLATE_ID, SIGN_IN_TEMPLATE_ID)
from wanglibao_rest.views import UdeskGenerator
from weixin.util import getAccountInfo
from wanglibao_pay.models import Bank, PayInfo
from wechatpy import parse_message, create_reply, WeChatClient
from wechatpy.replies import TransferCustomerServiceReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException, WeChatException
from wechatpy.oauth import WeChatOAuth
from weixin.common.decorators import weixin_api_error
from weixin.common.wx import generate_js_wxpay
from .models import Account, WeixinUser, WeixinAccounts, AuthorizeInfo, QrCode, SubscribeService, SubscribeRecord, WeiXinChannel, UserDailyActionRecord
# from .common.wechat import tuling
from decimal import Decimal
from wanglibao_pay.models import Card
from marketing.utils import get_channel_record
import json
import uuid
import urllib
import logging
import traceback
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.db import transaction, IntegrityError
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from wanglibao_p2p.common import get_p2p_list
from wanglibao_redis.backend import redis_backend
from rest_framework import renderers
from misc.models import Misc
from wechatpy.parser import parse_message
from wechatpy.messages import BaseMessage, TextMessage
import datetime, time
import base64
from .util import _generate_ajax_template
from wechatpy.events import (BaseEvent, ClickEvent, SubscribeScanEvent, ScanEvent, UnsubscribeEvent, SubscribeEvent,\
                             TemplateSendJobFinishEvent)
from experience_gold.models import ExperienceEvent, ExperienceEventRecord
from experience_gold.backends import SendExperienceGold
from wanglibao_profile.models import WanglibaoUserProfile
from weixin.tasks import detect_product_biding, sentTemplate
from weixin.util import sendTemplate, redirectToJumpPage, getOrCreateWeixinUser, bindUser, unbindUser, _process_scene_record, process_user_daily_action, getMiscValue
from weixin.util import FWH_UNBIND_URL, filter_emoji, get_weixin_code_url
from rest_framework.permissions import IsAuthenticated
from wanglibao_redis.backend import redis_backend
from misc.views import MiscRecommendProduction
from marketing.utils import pc_data_generator
from wanglibao_account.forms import BiSouYiRegisterForm
from util import FWH_LOGIN_URL
# from wanglibao_invite.models import WechatInviteRelation

logger = logging.getLogger("weixin")
logger_yuelibao = logging.getLogger('wanglibao_margin')

CHECK_BIND_CLICK_EVENT = ['subscribe_service', 'my_account', 'sign_in', 'my_experience_gold', 'customer_service']


CUSTOMER_SERVICE = '1'
SERVICE_SUBSCRIBE = '2'
OTHER_MENU = '3'
OTHER_TXT = '4'
Y_TXT = '5'


def stamp(dt):
    return long(time.mktime(dt.timetuple()))


def checkBindDeco(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        toUserName = self.msg._data['ToUserName']
        fromUserName = self.msg._data['FromUserName']
        user = kwargs.get('user')
        check_bind = False
        if isinstance(self.msg, BaseEvent):
            if isinstance(self.msg, (ClickEvent,)):
                if self.msg.key in CHECK_BIND_CLICK_EVENT:
                    check_bind = True
        elif isinstance(self.msg, BaseMessage):
            content = self.msg.content.lower()
            sub_service = SubscribeService.objects.filter(channel='weixin', is_open=True, key=content).first()
            if content == 'td' or sub_service:
                check_bind = True

        if check_bind and not user:
            txt = self.getBindTxt(fromUserName)
            reply = create_reply(txt, self.msg)
            return reply
        else:
            return func(self, *args, **kwargs)
    return wrapper


class WeixinJoinView(View):
    account = None

    def check_signature(self, request, account_key):
        # account = Account.objects.get(pk=account_key)#WeixinAccounts.get(account_key)
        weixin_account = WeixinAccounts.getByOriginalId(account_key)
        account = weixin_account.db_account
        # logger.debug(account_key + "============" + account.app_id+"=============="+account.token)
        try:
            check_signature(
                account.token,
                request.GET.get('signature'),
                request.GET.get('timestamp'),
                request.GET.get('nonce')
            )
        except InvalidSignatureException:
            return False

        return True

    def get(self, request, account_key):
        if not self.check_signature(request, account_key):
            return HttpResponseForbidden()

        return HttpResponse(request.GET.get('echostr'))

    def post(self, request, account_key):
        if not self.check_signature(request, account_key):
            return HttpResponseForbidden()
        # account = Account.objects.get(pk=account_key) #WeixinAccounts.get(account_key)
        self.msg = parse_message(request.body)
        msg = self.msg
        reply = None
        toUserName = msg._data['ToUserName']
        fromUserName = msg._data['FromUserName']
        createTime = msg._data['CreateTime']
        logger.debug("fromUserName:%s; MsgType:%s; Event:%s; EventKey:%s"%(fromUserName, msg._data.get('MsgType', "=="), msg._data.get('Event', "=="), msg._data.get('EventKey', "==")))
        weixin_account = WeixinAccounts.getByOriginalId(toUserName)
        w_user, old_subscribe = getOrCreateWeixinUser(fromUserName, weixin_account)
        user = w_user.user

        self.w_user = w_user

        if isinstance(msg, BaseEvent):
            # request.session['last_operate'] = OTHER_MENU
            if isinstance(msg, ClickEvent):
                reply = self.process_click_event(weixin_account, w_user=w_user, user=user)
            elif isinstance(msg, SubscribeEvent):
                self.process_user_operate(OTHER_MENU)
                reply = self.process_subscribe(old_subscribe, w_user=w_user, user=user)
            elif isinstance(msg, UnsubscribeEvent):
                self.process_user_operate(OTHER_MENU)
                if w_user.subscribe != 0:
                    w_user.subscribe = 0
                w_user.unsubscribe_time = int(time.time())
                if user:
                    unbindUser(w_user, user)
                reply = create_reply(u'欢迎下次关注我们！', msg)
            elif isinstance(msg, SubscribeScanEvent):
                self.process_user_operate(OTHER_MENU)
                reply = self.process_subscribe(old_subscribe, w_user=w_user, user=user)
            elif isinstance(msg, ScanEvent):
                self.process_user_operate(OTHER_MENU)
                #如果eventkey为用户id则进行绑定
                reply = self.process_subscribe(old_subscribe, w_user=w_user, user=user)
            elif isinstance(msg, TemplateSendJobFinishEvent):
                reply = -1
        elif isinstance(msg, BaseMessage):
            if isinstance(msg, TextMessage):
                reply = self.process_customer_transfer(weixin_account, w_user, user)
                # 自动回复  5000次／天
                # if not reply:
                #     if msg.content=='test':
                #         reply = -1
                #         product = P2PProduct.objects.get(id=1745)
                #         checkAndSendProductTemplate(product)
                # if not reply:
                #     reply = tuling(msg)
                # if not reply:
                #     # 多客服转接
                #     reply = TransferCustomerServiceReply(message=msg)
        if reply == -1 or not reply:
            return HttpResponse("")
        return HttpResponse(reply.render())

    def process_user_operate(self, operate):
        if False:
            try:
                redis = redis_backend()
                redis.redis.hset(self.msg._data['FromUserName'], "operate", operate)
                redis.redis.hset(self.msg._data['FromUserName'], "time", int(time.time()))

            except Exception,e:
                logger.debug("fromUserName:%s====%s" % (self.msg._data['FromUserName'], traceback.format_exc()))
        else:
            pass

    def process_customer_transfer(self, weixin_account, w_user, user):
        if False:
            try:
                redis = redis_backend()
                last_operate = redis.redis.hget(self.msg._data['FromUserName'], "operate")
                last_time = redis.redis.hget(self.msg._data['FromUserName'], "time")
                if last_time:
                    last_time = int(last_time)
                # print "operate:%s; last_time:%s"%(last_operate, last_time)
                reply = None
                txt = None
                is_customer_time = self.checkCsTime()
                if last_operate:
                    if last_operate == SERVICE_SUBSCRIBE:
                        reply = self.check_service_subscribe(w_user=w_user, user=user)
                        self.process_user_operate(OTHER_TXT)
                    elif last_operate == Y_TXT:
                        if time.time() - last_time <= 30*60*60:
                            reply = TransferCustomerServiceReply(message=self.msg)
                            self.process_user_operate(Y_TXT)
                    if last_operate == CUSTOMER_SERVICE:
                        if is_customer_time:
                            if self.msg.content.lower() == "y":
                                txt = "想问什么放马过来吧，简单描述下你想说的问题。"
                                self.process_user_operate(Y_TXT)
                            else:
                                txt = "如需联系人工客服请回复字母“Y”！聊什么听你的，但是网利君在线时间为工作日9：00~18：00。"
                        else:
                            txt = self.getCSReply()
                if not reply:
                    if not txt:
                        self.process_user_operate(OTHER_TXT)
                        if is_customer_time:
                            txt = "客官，想和网利君天南海北的聊天还是正经的咨询？点击在线客服，与网利君联系吧！网利君在线时间为工作日9：00~18：00。"
                        else:
                            txt = self.getCSReply()
                    client = WeChatClient(weixin_account.app_id, weixin_account.app_secret)
                    client.message._send_custom_message({
                                                "touser":self.msg._data['FromUserName'],
                                                "msgtype":"text",
                                                "text":
                                                {
                                                     "content":txt
                                                }
                                            }, account="007@wanglibao400")
                    reply = -1
            except Exception, e:
                reply = self.check_service_subscribe(w_user=w_user, user=user)
                if not reply:
                    reply = TransferCustomerServiceReply(message=self.msg)
                logger.debug("fromUserName:%s====%s" % (self.msg._data['FromUserName'], traceback.format_exc()))
        else:
            reply = self.check_service_subscribe(w_user=w_user, user=user)
        return reply

    def getCSReply(self):
        is_customer_time = self.checkCsTime()
        if is_customer_time:
            txt = u"如需联系人工客服请回复字母“Y”！聊什么听你的，但是网利君在线时间为工作日9：00~18：00。"
        else:
            txt = u"客官，网利君在线时间为\n"\
                    + u"【周一至周五9：00~18：00】，请在工作时间与我们联系哦~"
        return txt

    def checkCsTime(self):
        now = datetime.datetime.now()
        weekday = now.weekday() + 1
        if now.hour <= 18 and now.hour >= 9 and weekday >= 1 and weekday <= 5:
            return True
        return False

    @checkBindDeco
    def process_click_event(self, weixin_account, w_user=None, user=None):
        reply = None
        sub_services = SubscribeService.objects.filter(channel='weixin', is_open=True).all()
        toUserName = self.msg._data['ToUserName']
        fromUserName = self.msg._data['FromUserName']
        if self.msg.key == 'subscribe_service':
            txt = u'客官，请回复相关数字订阅最新项目通知，系统会在第一时间发送给您相关信息。\n'
            if len(sub_services)>0:
                for sub_service in sub_services:
                    txt += ("【" + sub_service.key + "】" + sub_service.describe + '\n')

                sub_records = SubscribeRecord.objects.filter(w_user=w_user, status=True, service__is_open=True)
                if sub_records.exists():
                    txt += u'已经订阅的项目：\n'
                    sub_records = sub_records.order_by('service').all()
                    for sub_record in sub_records:
                        txt += u"【" + sub_record.service.key + u"】"
                    txt += u'\n如需退订请回复TD'
                else:
                    txt += u'当前没有订阅任何项目'

                reply = create_reply(txt, self.msg)
            else:
                reply = -1
        if self.msg.key == 'bind_weixin':
            if not user:
                txt = self.getBindTxt(fromUserName)
            else:
                txt = self.getUnBindTxt(fromUserName, user.wanglibaouserprofile.phone)
            reply = create_reply(txt, self.msg)
        if self.msg.key == 'my_account':
            account_info = getAccountInfo(user)
            # 【账户概况】
            # 总资产       (元）： 12000.00
            # 可用余额（元）： 108.00
            # 累计收益（元）：  79.00
            # 待收收益（元）：  24.00
            now_str = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')
            infos = "%s元\n总资产　：%s元 \n可用余额：%s元" %(
                account_info['p2p_total_paid_interest'], account_info['total_asset'], account_info['p2p_margin'])
            a = MessageTemplate(ACCOUNT_INFO_TEMPLATE_ID, keyword1=now_str, keyword2=infos)
            sendTemplate(w_user, a)
            reply = -1
        if self.msg.key == 'customer_service':
            # self.request.session['last_operate'] = CUSTOMER_SERVICE

            udesk_obj = UdeskGenerator()
            try:
                phone = user.wanglibaouserprofile.phone
                udesk_url = udesk_obj.get_udesk_url(str(phone))
            except Exception, e:
                logger.debug('in process_click_event, get user error with : {}'.format(e.message))
                txt = self.getBindTxt(fromUserName)
                reply = create_reply(txt, self.msg)
                return reply
            reply = u"尊敬的用户您好, 确认联系客服, 请点击链接: <a href='%s'>【联系客服】</a>" % (udesk_url)

            reply = create_reply(reply, self.msg)

            # txt = self.getCSReply()
            # try:
            #     client = WeChatClient(weixin_account.app_id, weixin_account.app_secret)
            #     client.message._send_custom_message({
            #                                 "touser":fromUserName,
            #                                 "msgtype":"text",
            #                                 "text":
            #                                 {
            #                                      "content":txt
            #                                 }
            #                             }, account="007@wanglibao400")
            # except:
            #     pass
            # reply = -1#create_reply(txt, msg)

        if self.msg.key == 'month_papers':
            articles = self.getSubscribeArticle()
            reply = create_reply(articles, self.msg)

        if self.msg.key == 'sign_in':
            reply = self.process_sign_in(w_user, user)

        if self.msg.key == 'my_experience_gold':
            seg = SendExperienceGold(user)
            amount = seg.get_amount()
            txt = u"您的帐号：%s\n" \
                  u"体验金金额：%s元"%(user.wanglibaouserprofile.phone, amount)
            reply = create_reply(txt, self.msg)
        if self.msg.key == "customer_service":
            self.process_user_operate(CUSTOMER_SERVICE)
        elif self.msg.key == "subscribe_service":
            self.process_user_operate(SERVICE_SUBSCRIBE)
        else:
            self.process_user_operate(OTHER_MENU)
        return reply

    def process_sign_in(self, weixin_user, user, platform=u"weixin"):
        reply = -1
        try:
            ret_code, status, daily_record = process_user_daily_action(user, platform, action_type=u'sign_in')
            experience_amount = 0
            if daily_record.experience_record_id:
                experience_record = ExperienceEventRecord.objects.get(id=daily_record.experience_record_id)
                experience_amount=experience_record.event.amount
            reply_msg =u"%s，连续签到可获得更多奖励，记得明天再来哦！\n奖励金额：%s元体验金"
        # 签到时间：{{keyword1.DATA}}
        # 连续签到：{{keyword2.DATA}}
        # 累计签到：{{keyword3.DATA}}

            if ret_code == 1:
                txt = "今日你已签到，连续签到可获得更多奖励，记得明天再来哦！"
                reply = create_reply(txt, self.msg)
                # reply = -1
                # sentTemplate.apply_async(kwargs={"kwargs":json.dumps({
                #     "openid":weixin_user.openid,
                #     "template_id":SIGN_IN_TEMPLATE_ID,
                #     "first":reply_msg%(u"今日你已签到", experience_amount),
                #     "keyword1":timezone.localtime(daily_record.create_time).strftime("%Y-%m-%d %H:%M:%S"),
                #     "keyword2":"%s天" % daily_record.continue_days,
                #     "keyword3":"%s天" % UserDailyActionRecord.objects.filter(user=user, action_type=u'sign_in').count()
                # })},
                #                                 queue='celery02')
            elif ret_code == 0:
                reply = -1
                sentTemplate.apply_async(kwargs={"kwargs":json.dumps({
                    "openid":weixin_user.openid,
                    "template_id":SIGN_IN_TEMPLATE_ID,
                    "first":reply_msg%(u"恭喜您签到成功", experience_amount),
                    "keyword1":timezone.localtime(daily_record.create_time).strftime("%Y-%m-%d %H:%M:%S"),
                    "keyword2":"%s天" % daily_record.continue_days,
                    "keyword3":"%s天" % UserDailyActionRecord.objects.filter(user=user, action_type=u'sign_in').count()
                })},
                                                queue='celery02')
            else:
                reply = create_reply("签到失败", self.msg)

        except Exception,e:
            reply = create_reply("签到失败", self.msg)
            logger.debug(traceback.format_exc())
        return reply


    @checkBindDeco
    def check_service_subscribe(self, w_user=None, user=None):
        fromUserName = self.msg._data['FromUserName']
        content = self.msg.content.lower()
        reply = None
        txt = None
        if content == 'td':
            sub_records = SubscribeRecord.objects.filter(w_user=w_user, status=True)
            if sub_records.exists():
                sub_records.update(status=False, unsubscribe_time=int(time.time()))
                txt = u'订阅项目已退订成功，如需订阅相关项目，请再次点击【个性化项目】进行订阅'
            else:
                txt = u'您没有可退订项目，如需订阅相关项目，请再次点击【个性化项目】进行订阅'
            reply = create_reply(txt, self.msg)
            return reply
        sub_service = SubscribeService.objects.filter(channel='weixin', is_open=True, key=content).first()
        if sub_service:
            sub_service_record = SubscribeRecord.objects.filter(w_user=w_user, service = sub_service).first()
            if sub_service_record and sub_service_record.status==1:
                txt = u'客官真健忘，您已经订阅此项目通知，订阅其他上线通知项目吧～'
            if not sub_service_record:
                sub_service_record = SubscribeRecord()
                sub_service_record.service = sub_service
                sub_service_record.w_user = w_user
                sub_service_record.subscribe_time=int(time.time())
            if not sub_service_record.status:
                sub_service_record.status = True
                sub_service_record.subscribe_time=int(time.time())
                sub_service_record.save()
                txt = u'恭喜您，%s订阅成功，系统会在第一时间发送给您相关信息'%(sub_service.describe)
        else:
            if content.isdigit():
                txt = u'请回复正确的数字订阅项目'
            else:
                txt = u"请点击【在线客服】菜单，来与客服沟通。"
        if txt:
            reply = create_reply(txt, self.msg)
        return reply

    def process_subscribe(self, old_subscribe, w_user=None, user=None):
        fromUserName = self.msg._data['FromUserName']
        eventKey = self.msg._data['EventKey']
        reply = None

        #如果eventkey为用户id则进行绑定
        scene_id = None
        if eventKey:
            scene_id = eventKey
            if eventKey.isdigit():
                user_id = eventKey[:-3]
                channel_digital_code = eventKey[-3:]
                user = User.objects.filter(pk=int(user_id)).first()
                if user:
                    scene_id, reply = self.process_digital_code(w_user, user, channel_digital_code)
                    # rs, txt = bindUser(w_user, user)
                    # channel = WeiXinChannel.objects.filter(digital_code=channel_digital_code).first()
                    # if channel:
                    #     scene_id = channel.code
                    # reply = create_reply(txt, self.msg)
        if not old_subscribe and w_user.subscribe:
            w_user.scene_id = scene_id
            w_user.save()
            if scene_id:
                _process_scene_record(w_user, scene_id)

        if not reply:
            if not user:
                txt = self.getBindTxt(fromUserName)
                txt += u"\n网利宝自2014年8月上线以来，注册用户已突破130万人，投资额超过50亿元，目前已完成B轮融资！"
            else:
                txt = u"您的微信当前绑定的网利宝帐号为：%s"%user.wanglibaouserprofile.phone
            reply = create_reply(txt, self.msg)
        return reply

    def process_digital_code(self, w_user, user, channel_digital_code):
        share_invite_fwh_config = getMiscValue("share_invite_fwh_config")
        #share_invite_fwh_config = {"share_invite_digital_codes":[000], "articles":{"000":[{"image":"","url":"p={fp}","title":"","description":""}]}}
        channel = WeiXinChannel.objects.filter(digital_code=channel_digital_code).first()
        share_invite_digital_codes = share_invite_fwh_config["share_invite_digital_codes"]
        scene_id = channel_digital_code
        if channel:
            scene_id = channel.code
        if channel_digital_code in share_invite_digital_codes:
            inviter = user
            from wanglibao_profile.models import WanglibaoUserProfile
            profile = WanglibaoUserProfile.objects.filter(user=inviter).first()
            # WechatInviteRelation.objects.get_or_create(inviter=inviter, w_user_invited=w_user)
            articles = share_invite_fwh_config["articles"][channel_digital_code]
            for article in articles:
                article['url'] = settings.CALLBACK_HOST + article['url'].format(fp=base64.b64encode(profile.phone+"="))
                article['url'] = get_weixin_code_url(article['url'])
            reply = create_reply(articles, self.msg)
        else:
            rs, txt = bindUser(w_user, user)
            reply = create_reply(txt, self.msg)

        return scene_id, reply

    def getSubscribeArticle(self):
        big_data_img_url = "https://mmbiz.qlogo.cn/mmbiz/EmgibEGAXiahvyFZtnAQJ765uicv4VkX9gI8IlfkNibDj8un11ia7y8JZIWWk9LeKDNibaf0HbCDpia9sTO7WiaHHxRcNg/0?wx_fmt=jpeg"
        m = Misc.objects.filter(key='weixin_yuebao_info').first()
        big_data_url = 'http://mp.weixin.qq.com/s?__biz=MzA5NzE4NTIzMQ==&mid=400880736&idx=2&sn=8960f12d794c90492ed5cedd1561afc4&scene=1&srcid=1204pU1pDJsV4RyaK2WesNTN&key=ac89cba618d2d9768a249f64106fa7c4857db09c6013d1e43374d9c0dc4cfa7ba992e13d9b8c7826b109ee3729ef35a4&ascene=1&uin=MjU0MDYyNDQzMw%3D%3D&devicetype=webwx&version=70000001&pass_ticket=yHIDIChmoYlIXIUjkPF6XZwcg%2FcSi09vHTBNTyHS5BwL1%2B91EHyr90ZMXi3OEp4J'
        if m and m.value:
            info = json.loads(m.value)
            big_data_url = info['big_data_url']

        A_img_url = "https://mmbiz.qlogo.cn/mmbiz/EmgibEGAXiahvyFZtnAQJ765uicv4VkX9gIdMuibjodyEeWdavoBO0uvAdfpMzaCNjfreoT4APezdbu6hasMTibTWxw/0?wx_fmt=jpeg"
        A_url = "http://mp.weixin.qq.com/s?__biz=MjM5NTc0OTc5OQ==&mid=206425012&idx=1&sn=8ee1a55847e4a94d8c8941a7d051e821&scene=1&srcid=1201B5VHp3R7TDdlsog0bxFT&key=ac89cba618d2d976324fb9d2339235db9d6008530c972dec224dc69f371b8a75a6be336e5e4f2da34cd417cdd2b77ca6&ascene=1&uin=MjU0MDYyNDQzMw%3D%3D&devicetype=webwx&version=70000001&pass_ticket=5%2BegJdyHvw97jvM495sqVRvpdvtQ4vl9QykfsV21yy2tgNbUcnPTyAjchjglUkg3"

        B_img_url = "https://mmbiz.qlogo.cn/mmbiz/EmgibEGAXiahvyFZtnAQJ765uicv4VkX9gInibWxZlOdB2ZXn4lt1r0zEM8FgOXF9NkWo3K1hWwiaLeSH4JWics9IEvw/0?wx_fmt=jpeg"
        B_url = "http://mp.weixin.qq.com/s?__biz=MjM5NTc0OTc5OQ==&mid=206419904&idx=1&sn=6d0cf2bee4b110635c5a178be0241e6f&scene=1&srcid=12018c9ZzjIVDpAYiUMR9AQ2&key=ac89cba618d2d9765681b6b8e02f41f539b6d711d2c0c3c34ab5b5971c62c434ebd49e11b8c9cbd9f7372231fd6c0ca5&ascene=1&uin=MjU0MDYyNDQzMw%3D%3D&devicetype=webwx&version=70000001&pass_ticket=5%2BegJdyHvw97jvM495sqVRvpdvtQ4vl9QykfsV21yy2tgNbUcnPTyAjchjglUkg3"

        return [{'image':big_data_img_url, 'url':big_data_url, 'description':"网利宝10月数据公告", 'title':'大数据下的网利宝'},
                {'image':A_img_url, 'url':A_url, 'description':'IDG资本A轮千万美元融资', 'title':'IDG资本A轮千万美元融资'},
                {'image':B_img_url, 'url':B_url, 'description':'B轮4000万美元融资', 'title':'B轮4000万美元融资'},]

    def getBindTxt(self, fromUserName):
        bind_url = FWH_LOGIN_URL
        txt = u"终于等到你，还好我没放弃。绑定网利宝帐号，轻松投资、随时随地查看收益！\n" \
              u"<a href='%s'>【立即绑定】</a>" % (bind_url)
        return txt

    def getUnBindTxt(self, fromUserName, userPhone):
        txt = u"您的微信绑定帐号为：%s\n"%userPhone\
              + u"如需解绑当前帐号，请点击<a href='%s'>【立即解绑】</a>"%FWH_UNBIND_URL
        return txt

    def getSignExperience_gold(self):
        now = timezone.now()
        query_object = ExperienceEvent.objects.filter(invalid=False, give_mode='weixin_sign_in',
                                                      available_at__lt=now, unavailable_at__gt=now)
        experience_events = query_object.order_by('amount').all()
        length = len(experience_events)
        if length > 1:
            random_int = random.randint(0, length-1)
            return experience_events[random_int]
        return None

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WeixinJoinView, self).dispatch(request, *args, **kwargs)


class WeixinLogin(TemplateView):
    template_name = 'weixin_login.jade'

    def get_context_data(self, **kwargs):
        context = super(WeixinLogin, self).get_context_data(**kwargs)
        code = self.request.GET.get('code')

        if code:
            account_id = self.request.GET.get('state')
            try:
                account = Account.objects.get(pk=account_id)
            except Account.DoesNotExist:
                return HttpResponseNotFound()

            try:
                oauth = WeChatOAuth(account.app_id, account.app_secret)
                res = oauth.fetch_access_token(code)
                account.oauth_access_token = res.get('access_token')
                account.oauth_access_token_expires_in = res.get('expires_in')
                account.oauth_refresh_token = res.get('refresh_token')
                account.save()
                WeixinUser.objects.get_or_create(openid=res.get('openid'))
                context['openid'] = res.get('openid')
            except WeChatException, e:
                pass
        next = self.request.GET.get('next', '')
        next = urllib.unquote(next.encode('utf-8'))
        return {
            'context': context,
            'next': next
            }


class WeixinCoopLogin(TemplateView):
    template_name = 'weixin_login.jade'

    def get_context_data(self, **kwargs):
        context = super(WeixinCoopLogin, self).get_context_data(**kwargs)
        code = self.request.GET.get('code')
        token = self.request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, '')

        if token:
            tp_name = 'weixin_login_%s.jade' % token.lower()
            try:
                get_template(tp_name)
                self.template_name = tp_name
            except TemplateDoesNotExist:
                pass

        if code:
            account_id = self.request.GET.get('state')
            try:
                account = Account.objects.get(pk=account_id)
            except Account.DoesNotExist:
                return HttpResponseNotFound()

            try:
                oauth = WeChatOAuth(account.app_id, account.app_secret)
                res = oauth.fetch_access_token(code)
                account.oauth_access_token = res.get('access_token')
                account.oauth_access_token_expires_in = res.get('expires_in')
                account.oauth_refresh_token = res.get('refresh_token')
                account.save()
                WeixinUser.objects.get_or_create(openid=res.get('openid'))
                context['openid'] = res.get('openid')
            except WeChatException, e:
                pass
        next = self.request.GET.get('next', '')
        next = urllib.unquote(next.encode('utf-8'))

        phone = ''
        if token == 'bisouyi':
            form = BiSouYiRegisterForm(self.request.session, action='old_login')
            if form.is_valid():
                phone = form.get_phone()
                next = form.get_other()

        return {
            'context': context,
            'next': next,
            'phone': phone,
            }


class WeixinRegister(TemplateView):
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
        return {
            'token': token,
            'channel': channel,
            'phone': phone,
            'next' : next
        }

class ChannelRegister(TemplateView):
    template_name = 'channel_register.jade'

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
        # 网站数据
        m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_PC_DATA, desc=MiscRecommendProduction.DESC_PC_DATA)
        site_data = m.get_recommend_products()
        if site_data:
            site_data = site_data[MiscRecommendProduction.KEY_PC_DATA]
        else:
            site_data = pc_data_generator()
            m.update_value(value={MiscRecommendProduction.KEY_PC_DATA: site_data})

        next = self.request.GET.get('next', '')
        return {
            'token': token,
            'channel': channel,
            'next': next,
            'site_data': site_data
        }



class WeixinCoopRegister(TemplateView):
    template_name = 'weixin_regist_new.jade'

    def get_context_data(self, **kwargs):
        token = self.request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, '')
        token_session = self.request.session.get(settings.PROMO_TOKEN_QUERY_STRING, '')

        if token:
            tp_name = 'service_regist_%s.jade' % token.lower()
            try:
                get_template(tp_name)
                self.template_name = tp_name
            except TemplateDoesNotExist:
                pass
        elif token_session:
            token = token_session
        else:
            token = 'weixin'

        if token:
            channel = get_channel_record(token)
        else:
            channel = None

        phone = self.request.GET.get('phone', 0)
        _next = self.request.GET.get('next', '')

        return {
            'token': token,
            'channel': channel,
            'phone': phone,
            'next': _next
        }


class WeixinRegisterBindCard(TemplateView):
    template_name = 'weixin_registProcess_second.jade'

    permission_classes = (IsAuthenticated, )

    def get_context_data(self, **kwargs):

        user = self.request.user

        pay_info = PayInfo.objects.filter(user=user)

        recharge = None
        if pay_info.filter(status="成功"):
            recharge = True
        else:
            recharge = False

        return {
            'recharge': recharge
        }

class JumpPageTemplate(TemplateView):
    template_name = 'sub_times.jade'

    def get_context_data(self, **kwargs):
        context = super(JumpPageTemplate, self).get_context_data(**kwargs)
        message = self.request.GET.get('message', 'ERROR')
        message=message.encode('utf-8')
        message = urllib.unquote(message)
        context['message'] = message
        return {
            'context': context,
            'next': next
            }

class WeixinBind(TemplateView):
    template_name = 'sub_times.jade'

    def get_context_data(self, **kwargs):
        context = super(WeixinBind, self).get_context_data(**kwargs)
        user = self.request.user
        rs = -1
        txt = 'error'
        try:
            openid = self.request.GET.get('openid')
            weixin_user = WeixinUser.objects.get(openid=openid)
            rs, txt = bindUser(weixin_user, user)
        except WeixinUser.DoesNotExist, e:
            logger.debug("*************************"+e.message)
        context['message'] = txt
        return {
            'context': context,
            'next': next
            }



class UnBindWeiUser(TemplateView):
    template_name = 'sub_is_bind.jade'

    def get_context_data(self, **kwargs):
        context = super(UnBindWeiUser, self).get_context_data(**kwargs)
        next = self.request.GET.get('next', '')
        return {
            'context': context,
            'next': next
            }

    def dispatch(self, request, *args, **kwargs):
        code = request.GET.get('code')
        state = request.GET.get('state')
        error_msg = ""
        try:
            if code and state:
                account = WeixinAccounts.getByOriginalId(state)
                request.session['account_key'] = account.key
                oauth = WeChatOAuth(account.app_id, account.app_secret, )
                res = oauth.fetch_access_token(code)
                self.openid = res.get('openid')
                request.session['openid'] = self.openid
                w_user = WeixinUser.objects.filter(openid=self.openid).first()
                if not w_user:
                    message = u"请从[服务中心]点击[账号关联]进行绑定"
                    return redirectToJumpPage(message)
                if not w_user.user:
                    return redirectToJumpPage(u"您没有绑定的网利宝帐号")
            else:
                error_msg='code or state not in request'
        except WeChatException, e:
            error_msg = e.message
        if error_msg:
            return redirectToJumpPage(error_msg)
        else:
            return super(UnBindWeiUser, self).dispatch(request, *args, **kwargs)

class UnBindWeiUserAPI(APIView):
    permission_classes = ()
    http_method_names = ['post']

    def post(self, request):
        openid = request.session.get('openid')
        if not openid:
            return Response({'message':'openid not in session'})
        weixin_user = WeixinUser.objects.get(openid=openid)
        if weixin_user.user:
            user = weixin_user.user
            user_phone = user.wanglibaouserprofile.phone
            unbindUser(weixin_user, user)
            now_str = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')
            logout(request)
            sentTemplate.apply_async(kwargs={"kwargs":json.dumps({
                    "openid":weixin_user.openid,
                    "template_id":UNBIND_SUCCESS_TEMPLATE_ID,
                    "keyword1":user_phone,
                    "keyword2":now_str
                })},
                                                queue='celery02')
        return Response({'message':'ok'})


class WeixinJsapiConfig(APIView):
    permission_classes = ()
    http_method_names = ['get']

    @weixin_api_error
    def get(self, request):
        if settings.ENV == settings.ENV_PRODUCTION:
            request.session['account_key'] = 'sub_1'
            account = WeixinAccounts.get('sub_1')
        else:
            request.session['account_key'] = 'test'
            account = WeixinAccounts.get('test')

        noncestr = uuid.uuid1().hex
        timestamp = str(int(time.time()))
        url = (request.META.get('HTTP_REFERER') or '').split('#')[0]

        app_id = account.app_id
        signature = account.weixin_client.jsapi.get_jsapi_signature(
            noncestr,
            account.jsapi_ticket,
            timestamp,
            url
        )

        data = {
            'appId': app_id,
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'signature': signature
        }
        return Response(data)


class WeixinLoginAPI(APIView):
    permission_classes = ()
    http_method_names = ['post']

    def _form(self, request):
        return LoginAuthenticationNoCaptchaForm(request, data=request.POST)

    def post(self, request):
        # add by ChenWeiBin@20160113
        phone = request.POST.get('identifier', '')
        profile = WanglibaoUserProfile.objects.filter(phone=phone, utype='3').first()
        if profile:
            return Response({
                "code": u"企业用户请在PC端登录",
            }, status=400)

        form = self._form(request)

        if form.is_valid():
            user = form.get_user()
            try:
                openid = request.POST.get('openid')
                if openid:
                    weixin_user = WeixinUser.objects.get(openid=openid)
                    # rs, txt = bindUser(weixin_user, user)
            except WeixinUser.DoesNotExist:
                pass

            auth_login(request, user)
            request.session.set_expiry(1800)
            data = {'nickname': user.wanglibaouserprofile.nick_name}
            return Response(data)

        return Response(form.errors, status=400)


class WeixinOauthLoginRedirect(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            account = Account.objects.first()
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


class WeixinPayTest(TemplateView):
    template_name = 'pay_test.html'

    def get_context_data(self, **kwargs):
        context = super(WeixinPayTest, self).get_context_data(**kwargs)
        js_wxpay = generate_js_wxpay(self.request)
        code = self.request.GET.get('code')
        openid = js_wxpay.generate_openid(code)
        context['openid'] = openid
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.GET.get('code'):
            info_dict = {
                'redirect_uri': request.build_absolute_uri(reverse('weixin_pay_test')),
                'state': '123',
            }
            js_wxpay = generate_js_wxpay(request)
            url = js_wxpay.generate_redirect_url(info_dict)
            return HttpResponseRedirect(url)

        return super(WeixinPayTest, self).dispatch(request, *args, **kwargs)


class WeixinPayOrder(APIView):
    permission_classes = ()
    http_method_names = ['post']

    def post(self, request):
        product = {
            'attach': u'网利宝微信支付测试1分',
            'body': u'网利宝微信支付测试1分',
            'out_trade_no': uuid.uuid1().hex,
            'total_fee': 0.01,
        }
        js_wxpay = generate_js_wxpay(request)
        data = js_wxpay.generate_jsapi(product, request.POST.get('openid'))
        return Response(data)


class WeixinPayNotify(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        js_wxpay = generate_js_wxpay(request)
        xml_str = request.body
        print 'xml_str: {}'.format(xml_str)
        ret, ret_dict = js_wxpay.verify_notify(xml_str)
        print 'ret: {}'.format(ret)
        print 'ret_dict: ', ret_dict
        # 在这里添加订单更新逻辑
        if ret:
            ret_dict = {
                'return_code': 'SUCCESS',
                'return_msg': 'OK',
            }
            ret_xml = js_wxpay.generate_notify_resp(ret_dict)
        else:
            ret_dict = {
                'return_code': 'FAIL',
                'return_msg': 'verify error',
            }
            ret_xml = js_wxpay.generate_notify_resp(ret_dict)

        print 'ret_xml: {}'.format(ret_xml)
        return HttpResponse(ret_xml)


class P2PListView(TemplateView):
    template_name = 'weixin_list.jade'

    def get_context_data(self, **kwargs):
        token = self.request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, '')

        if token:
            tp_name = 'weixin_list_%s.jade' % token.lower()
            try:
                get_template(tp_name)
                self.template_name = tp_name
            except TemplateDoesNotExist:
                pass

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
        except Exception:
            p2p_products = paginator.page(paginator.num_pages)

        now = timezone.now()
        banner = Banner.objects.filter(device='weixin', type='banner', is_used=True)\
            .filter(Q(is_long_used=True) | Q(start_at__lt=now, end_at__gt=now)).order_by('-priority')[:3]

        return {
            'results': p2p_products[:10],
            'banner': banner,
        }


class P2PListWeixin(APIView):
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

        html_data = _generate_ajax_template(p2p_products, 'include/ajax/ajax_list.jade')

        return Response({
            'html_data': html_data,
            'page': page,
            'pagesize': pagesize,
        })


class P2PDetailView(TemplateView):
    source = ""
    def get_template_names(self):
        template = self.kwargs['template']
        if template == 'calculator':
            template_name = 'weixin_calculator.jade'
        elif template == 'buy':
            template_name = 'weixin_buy.jade'
        else:
            template_name = 'weixin_detail.jade'
            if self.source=='fwh':
                template_name = 'service_detail.jade'

        return template_name

    def get_context_data(self, id, **kwargs):
        context = super(P2PDetailView, self).get_context_data(**kwargs)

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

        if p2p['soldout_time']:
            end_time = p2p['soldout_time']
        else:
            end_time = p2p['end_time']

        terms = get_amortization_plan(p2p['pay_method']).generate(p2p['total_amount'],
                                                               p2p['expected_earning_rate'] / 100,
                                                               datetime.datetime.now(),
                                                               p2p['period'])
        total_earning = terms.get('total') - p2p['total_amount']
        total_fee_earning = 0

        if p2p['activity']:
            total_fee_earning = Decimal(p2p['total_amount'] * p2p['activity']['activity_rule_amount'] *
                                        (Decimal(p2p['period']) / Decimal(12))).quantize(Decimal('0.01'))

        user_margin = 0
        current_equity = 0
        redpacks = []
        user = self.request.user
        id_is_valid = False
        is_one = False
        is_bind = False
        if user.is_authenticated():
            user_margin = user.margin.margin
            equity_record = P2PEquity.objects.filter(product=p2p['id']).filter(user=user).first()
            if equity_record is not None:
                current_equity = equity_record.equity

            device = utils.split_ua(self.request)
            result = backends.list_redpack(user, 'available', device['device_type'], p2p['id'])
            redpacks = result['packages'].get('available', [])
            id_is_valid = user.wanglibaouserprofile.id_is_valid,
            try:
                p2p_cards = card_bind_list(self.request)['cards']
                for card in p2p_cards:
                    is_bind = True
                    if card['is_the_one_card']:
                        is_one = True
            except:
                pass

        orderable_amount = min(p2p['limit_amount_per_user'] - current_equity, p2p['remain'])
        total_buy_user = P2PEquity.objects.filter(product=p2p['id']).count()

        amount = self.request.GET.get('amount', 0)
        amount_profit = self.request.GET.get('amount_profit', 0)
        next = self.request.GET.get('next', '')
        context.update({
            'p2p': p2p,
            'end_time': end_time,
            'orderable_amount': orderable_amount,
            'total_earning': total_earning,
            'current_equity': current_equity,
            'attachments': p2p['attachments'],
            'total_fee_earning': total_fee_earning,
            'total_buy_user': total_buy_user,
            'margin': float(user_margin),
            'amount': float(amount),
            'redpacks': redpacks,
            'next': next,
            'amount_profit': amount_profit,
            'id_is_valid':id_is_valid,
            'is_one':is_one,
            'is_bind':is_bind
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            if self.kwargs['template'] == 'buy':
                #未登录状态下buy模板不需要取 amount 和 amount_profit
                #amount = request.GET.get('amount', '')
                #amount_profit = request.GET.get('amount_profit', '')
                #next_str = '?amount=%s&amount_profit=%s' % (amount, amount_profit)
                redirect_str = '/weixin/login/?next=/weixin/view/buy/%s/' % (self.kwargs['id'],)
                return HttpResponseRedirect(redirect_str)
        return super(P2PDetailView, self).dispatch(request, *args, **kwargs)


class WeixinAccountHome(TemplateView):
    template_name = 'weixin_account_new.jade'

    def get_context_data(self, **kwargs):
        user = self.request.user

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        unpayed_principle = 0
        p2p_total_paid_interest = 0
        p2p_total_unpaid_interest = 0
        p2p_total_interest = 0
        p2p_total_coupon_interest = 0
        p2p_total_paid_coupon_interest = 0
        p2p_total_unpaid_coupon_interest = 0
        p2p_activity_interest = 0
        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal  # 待收本金
                p2p_total_paid_interest += equity.pre_paid_interest  # 累积收益
                p2p_total_unpaid_interest += equity.unpaid_interest  # 待收益
                p2p_total_interest += equity.pre_total_interest  # 总收益
                p2p_activity_interest += equity.activity_interest  # 活动收益
                p2p_total_coupon_interest += equity.pre_total_coupon_interest  # 加息券总收益
                p2p_total_paid_coupon_interest += equity.pre_paid_coupon_interest  # 加息券已收总收益
                p2p_total_unpaid_coupon_interest += equity.unpaid_coupon_interest  # 加息券待收总收益

        p2p_margin = user.margin.margin  # P2P余额
        p2p_freeze = user.margin.freeze  # P2P投资中冻结金额
        p2p_withdrawing = user.margin.withdrawing  # P2P提现中冻结金额
        p2p_unpayed_principle = unpayed_principle  # P2P待收本金

        # 增加从PHP项目来的月利宝待收本金
        url = 'https://' + self.request.get_host() + settings.PHP_UNPAID_PRINCIPLE_BASE
        try:
            if int(self.request.get_host().split(':')[1]) > 7000:
                url = settings.PHP_APP_INDEX_DATA_DEV
        except Exception, e:
            pass

        php_principle = get_php_redis_principle(user.pk, url)
        p2p_unpayed_principle += php_principle

        # 增加从PHP项目来的 昨日收益, 累计收益, 待收收益
        url = 'https://' + self.request.get_host() + settings.PHP_APP_INDEX_DATA
        try:
            if int(self.request.get_host().split(':')[1]) > 7000:
                url = settings.PHP_APP_INDEX_DATA_DEV
        except Exception, e:
            pass

        try:
            index_data = get_php_index_data(url, user.id)
        except Exception, e:
            index_data = {"yesterdayIncome": 0, "paidIncome": 0, "unPaidIncome": 0}
            logger_yuelibao.debug(u'in WeixinAccountHome, 月利宝地址请求失败!!! exception = {}'.format(e.message))

        p2p_total_asset = p2p_margin + p2p_freeze + p2p_withdrawing + p2p_unpayed_principle

        fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)
        fund_total_asset = 0
        if fund_hold_info.exists():
            for hold_info in fund_hold_info:
                fund_total_asset += hold_info.current_remain_share + hold_info.unpaid_income

        banner = Banner.objects.filter(device='weixin', type='banner', is_used=True).order_by('-priority').first()

        return {
            'total_asset': p2p_total_asset + fund_total_asset,  # 总资产
            'p2p_total_asset': p2p_total_asset,  # p2p总资产
            'p2p_margin': p2p_margin,  # P2P余额
            'p2p_freeze': p2p_freeze,  # P2P投资中冻结金额
            'p2p_withdrawing': p2p_withdrawing,  # P2P提现中冻结金额
            'p2p_unpayed_principle': p2p_unpayed_principle,  # P2P待收本金
            'p2p_total_unpaid_interest': p2p_total_unpaid_interest + p2p_total_unpaid_coupon_interest +
                                         Decimal(index_data['unPaidIncome']),  # p2p总待收益
            'p2p_total_paid_interest': p2p_total_paid_interest + p2p_activity_interest +
                                       p2p_total_paid_coupon_interest + Decimal(index_data['paidIncome']),  # P2P总累积收益
            'p2p_total_interest': p2p_total_interest + p2p_total_coupon_interest,  # P2P总收益
            'banner': banner,
        }


class WeixinRecharge(TemplateView):
    template_name = 'weixin_recharge.jade'

    def get_context_data(self, **kwargs):

        banks = Bank.get_kuai_deposit_banks()
        next = self.request.GET.get('rechargeNext', '')
        user = self.request.user

        pay_info = PayInfo.objects.filter(user=user)

        recharge = None
        if pay_info.filter(status="成功"):
            recharge = True
        else:
            recharge = False
        return {
            'recharge': recharge,
            'banks': banks,
            'next' : next,
        }


class WeixinRechargeSecond(TemplateView):
    template_name = 'weixin_recharge_second.jade'

    def get_context_data(self, **kwargs):
        card_no = self.request.GET.get('card_no', '')
        gate_id = self.request.GET.get('gate_id', '')
        amount = self.request.GET.get('amount', 0)
        user = self.request.user.wanglibaouserprofile
        try:
            bank = Bank.objects.filter(gate_id=gate_id).first()
        except:
            bank = None
        next = self.request.GET.get('rechargeNext', '')
        context = {
            'card_no': card_no,
            'gate_id': gate_id,
            'amount': amount,
            'bank': bank,
            'user': user,
            'next': next,
        }
        return context


class WeixinTransaction(TemplateView):
    template_name = 'weixin_transaction.jade'
    source = 'weixin'
    def get_template_names(self):
        status = self.kwargs['status']
        if status == 'buying':
            template_name = 'weixin_transaction_buying.jade'
            if self.source=='fwh':
                template_name = 'service_transaction_buying.jade'
        elif status == 'finished':
            template_name = 'weixin_transaction_finished.jade'
            if self.source=='fwh':
                template_name = 'service_transaction_finished.jade'
        else:
            template_name = 'weixin_transaction.jade'
            if self.source=='fwh':
                template_name = 'service_transaction_repay.jade'
        return template_name

    def get_context_data(self, status, **kwargs):
        if status not in ['repaying', 'buying', 'finished']:
            return Response({'ret_code': 20400, 'message': u'标的状态错误'})
        has_link = False
        if status == 'repaying':
            has_link = True
            p2p_status = u'还款中'
        elif status == 'finished':
            p2p_status = u'已完成'
        else:
            p2p_status = u'正在招标'
        if status == 'buying':
            p2p_equities = P2PEquity.objects.filter(user=self.request.user).filter(product__status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'正在招标',
            ]).select_related('product')[:10]
        else:
            p2p_equities = P2PEquity.objects.filter(user=self.request.user).filter(product__status=p2p_status) \
                .select_related('product')[:10]

        p2p_records = [{
            'equity_created_at': timezone.localtime(equity.created_at).strftime("%Y.%m.%d %H:%M:%S"),  # 投标时间
            'equity_product_short_name': equity.product.short_name,  # 产品名称
            'equity_product_expected_earning_rate': equity.product.expected_earning_rate,  # 年化收益(%)
            'equity_product_period': equity.product.period,  # 产品期限(月)*
            'equity_equity': float(equity.equity),  # 用户所持份额(投资金额)
            'equity_product_display_status': equity.product.display_status,  # 状态
            'equity_term': equity.term,  # 还款期
            'equity_product_amortization_count': equity.product.amortization_count,  # 还款期数
            'equity_paid_interest': float(equity.pre_paid_interest + equity.pre_paid_coupon_interest),  # 单个已经收益
            'equity_total_interest': float(equity.pre_total_interest + equity.pre_total_coupon_interest),  # 单个预期收益
            'equity_will_interest': float(equity.pre_total_interest - equity.pre_paid_interest + equity.unpaid_coupon_interest),
            'equity_contract': 'https://%s/api/p2p/contract/%s/' % (
                self.request.get_host(), equity.product.id),  # 合同
            'product_id': equity.product_id,
            'has_link': has_link,
        } for equity in p2p_equities]

        return {
            'status': {
                'chinese': p2p_status,
                'english': status
            },
            'results': p2p_records
        }


class WeixinP2PRecordAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        get_status = request.GET.get('status', 'repaying')
        if get_status not in ['repaying', 'buying', 'finished']:
            return Response({'ret_code': 20400, 'message': u'标的状态错误'})
        has_link = False
        if get_status == 'repaying':
            has_link = True
            p2p_status = u'还款中'
        elif get_status == 'finished':
            p2p_status = u'已完成'
        else:
            p2p_status = u'正在招标'
        page = request.GET.get('page', 1)
        pagesize = request.GET.get('pagesize', 10)
        page = int(page)
        pagesize = int(pagesize)

        if get_status == 'buying':
            p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'正在招标',
            ]).select_related('product')[(page-1)*pagesize:page*pagesize]
        else:
            p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status=p2p_status)\
                .select_related('product')[(page-1)*pagesize:page*pagesize]

        p2p_records = [{
             'equity_created_at': timezone.localtime(equity.created_at).strftime("%Y-%m-%d %H:%M:%S"),  # 投标时间
             'equity_product_short_name': equity.product.short_name,  # 产品名称
             'equity_product_expected_earning_rate': equity.product.expected_earning_rate,  # 年化收益(%)
             'equity_product_period': equity.product.period,  # 产品期限(月)*
             'equity_equity': float(equity.equity),  # 用户所持份额(投资金额)
             'equity_product_display_status': equity.product.display_status,  # 状态
             'equity_term': equity.term,  # 还款期
             'equity_product_amortization_count': equity.product.amortization_count,  # 还款期数
             'equity_paid_interest': float(equity.pre_paid_interest),  # 单个已经收益
             'equity_total_interest': float(equity.pre_total_interest),  # 单个预期收益
             'equity_contract': 'https://%s/api/p2p/contract/%s/' % (
                 request.get_host(), equity.product.id),  # 合同
             'product_id': equity.product_id,
             'has_link': has_link,
        } for equity in p2p_equities]

        html_data = _generate_ajax_template(p2p_records, 'include/ajax/ajax_transaction.jade')

        return Response({
            'html_data': html_data,
            'page': page,
            'pagesize': pagesize,
        })


class WeixinAccountSecurity(TemplateView):
    template_name = 'weixin_security.jade'

    def get_context_data(self, **kwargs):
        is_one = ''
        try:
            p2p_cards = card_bind_list(self.request)['cards']
            for card in p2p_cards:
                if card['is_the_one_card']:
                    is_one = True
            if is_one:
                card_count = 1
            else:
                card_count = len(p2p_cards)
        except:
            card_count = 0

        return {
            'p2p_cards': card_count,
            'is_one': is_one
        }

class WeixinAccountBankCard(TemplateView):
    template_name = 'weixin_bankcard.jade'

    def get_context_data(self, **kwargs):
        is_one = ''
        p2p_cards = ''
        try:
            p2p_cards = card_bind_list(self.request)['cards']
            for card in p2p_cards:
                if card['is_the_one_card']:
                    is_one = True
        except:
            result = ''

        user = self.request.user

        pay_info = PayInfo.objects.filter(user=user)

        recharge = None
        if pay_info.filter(status="成功"):
            recharge = True
        else:
            recharge = False
        return {
            'recharge': recharge,
            'p2p_cards': p2p_cards,
            'is_one': is_one
        }


class WeixinAccountBankCardAdd(TemplateView):
    template_name = 'weixin_bankcard_add.jade'

    def get_context_data(self, **kwargs):
        banks = Bank.get_withdraw_banks()
        return {
            'banks': banks,
        }


class AuthorizeCode(APIView):
    permission_classes = ()

    def get(self, request):
        account_id = self.request.GET.get('state')
        if not account_id:
            return Response({'errcode':-1, 'errmsg':'state is null'})
        try:
            account = None
            weixin_account = WeixinAccounts.getByOriginalId(account_id)
            if weixin_account:
                account = weixin_account.db_account
            if not account:
                account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            return HttpResponseNotFound()
        auth = request.GET.get('auth')
        redirect_uri = settings.WEIXIN_CALLBACK_URL + reverse("weixin_authorize_user_info")
        count = 0
        for key in request.GET.keys():
            if key == u'state':
                continue
            if count == 0:
                redirect_uri += '?%s=%s'%(key, request.GET.get(key))
            else:
                redirect_uri += "&%s=%s"%(key, request.GET.get(key))
            count += 1
        print redirect_uri
        # print redirect_uri
        if auth and auth == '1':
            oauth = WeChatOAuth(account.app_id, account.app_secret, redirect_uri=redirect_uri, scope='snsapi_userinfo', state=account_id)
        else:
            oauth = WeChatOAuth(account.app_id, account.app_secret, redirect_uri=redirect_uri, state=account_id)
        return redirect(oauth.authorize_url)


class AuthorizeUser(APIView):
    permission_classes = ()
    def get(self, request):
        account_id = self.request.GET.get('state', "0")
        try:
            account = None
            weixin_account = WeixinAccounts.getByOriginalId(account_id)
            if weixin_account:
                account = weixin_account.db_account
            if not account:
                account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            return HttpResponseNotFound()
        redirect_uri = self.request.GET.get('redirect_uri')
        redirect_url = ''
        if redirect_uri:
            redirect_url = urllib.unquote(redirect_uri)
        if not redirect_url:
            return Response({'errcode':-1,  'errmsg':'need a redirect_uri'})
        code = request.GET.get('code')
        oauth = WeChatOAuth(account.app_id, account.app_secret, )
        if code:
            try:
                res = oauth.fetch_access_token(code)
            except WeChatException, e:
                return Response({'errcode':e.errcode, 'errmsg':e.errmsg})
            openid = res.get('openid')
            try:
                w_user = WeixinUser.objects.filter(openid=openid).first()
                save_user = False
                if not w_user:
                    w_user = WeixinUser()
                    w_user.account_original_id = account.original_id
                    w_user.openid = openid
                    w_user.save()

                if w_user.account_original_id != account.original_id:
                    w_user.account_original_id = account.original_id
                    save_user = True

                if not w_user.auth_info:
                    auth_info = AuthorizeInfo()
                    auth_info.access_token = res.get('access_token')
                    auth_info.access_token_expires_at = Account._now() + datetime.timedelta(seconds=res.get('expires_in') - 60)
                    auth_info.refresh_token = res.get('refresh_token')
                    auth_info.save()
                    w_user.auth_info = auth_info
                    save_user = True
                else:
                    w_user.auth_info.access_token = res.get('access_token')
                    w_user.auth_info.access_token_expires_at = Account._now() + datetime.timedelta(seconds=res.get('expires_in') - 60)
                    w_user.auth_info.refresh_token = res.get('refresh_token')
                    w_user.auth_info.save()
                if save_user:
                    w_user.save()
            except IntegrityError, e:
                logger.debug(traceback.format_exc())

            appendkeys = []
            for key in request.GET.keys():
                if key == u'state' or key == u'code' or key== u'redirect_uri':
                    continue
                appendkeys.append(key)

            if redirect_url.find('?') == -1:
                redirect_url += '?openid=%s'%openid
            else:
                redirect_url += '&openid=%s'%openid
            for key in appendkeys:
                redirect_url += '&%s=%s'%(key, request.GET.get(key))
            return redirect(redirect_url)
        return Response({'errcode':-2, 'errmsg':'code is null'})


class GetAuthUserInfo(APIView):
    permission_classes = ()
    def get(self, request):
        openid = request.GET.get('openid')
        if not openid:
            return Response({'errcode':-3, 'errmsg':'openid is null'})
        w_user = WeixinUser.objects.filter(openid=openid).first()
        if not w_user:
            return Response({'errcode':-4, 'errmsg':'openid is not exist'})
        if w_user.nickname:

            return Response({
                       "openid":openid,
                       "nickname": w_user.nickname,
                       "sex": w_user.sex,
                       "province": w_user.province,
                       "city": w_user.city,
                       "country": w_user.country,
                        "headimgurl": w_user.headimgurl,
                        "unionid": w_user.unionid,
                    })
        if not w_user.auth_info:
            return Response({'errcode':-5, 'errmsg':'openid auth info is null'})
        # print w_user.account_original_id
        weixin_account = WeixinAccounts.getByOriginalId(w_user.account_original_id)
        try:
            oauth = WeChatOAuth(weixin_account.app_id, weixin_account.app_secret, )
            if not w_user.auth_info.check_access_token():
                res = oauth.refresh_access_token(w_user.auth_info.refresh_token)
                w_user.auth_info.access_token = res['access_token']
                w_user.auth_info.refresh_token = res['refresh_token']
                w_user.auth_info.access_token_expires_at = Account._now() + datetime.timedelta(seconds=res.get('expires_in') - 60)
                w_user.auth_info.save()
            user_info = oauth.get_user_info(w_user.openid, w_user.auth_info.access_token)
            w_user.nickname = user_info.get('nickname', "")
            w_user.sex = user_info.get('sex', 0)
            w_user.city = user_info.get('city', "")
            w_user.country = user_info.get('country', "")
            w_user.headimgurl = user_info.get('headimgurl', "")
            w_user.unionid = user_info.get('unionid', "")
            w_user.province = user_info.get('province', "")
            w_user.subscribe = user_info.get('subscribe', 0)
            w_user.subscribe_time = user_info.get('subscribe_time', 0)
            w_user.nickname = filter_emoji(w_user.nickname, "*")
            w_user.save()
            return Response(user_info)
        except WeChatException, e:
            return Response({'errcode':e.errcode, 'errmsg':e.errmsg})


class GetUserInfo(APIView):
    renderer_classes = (renderers.UnicodeJSONRenderer,)
    permission_classes = ()

    @weixin_api_error
    def get(self, request):
        openid = request.GET.get('openid')
        if not openid:
            return Response({'errcode':-3, 'errmsg':'openid is null'})
        w_user = WeixinUser.objects.filter(openid=openid).first()
        if not w_user:
            return Response({'errcode':-4, 'errmsg':'openid is not exist'})
        weixin_account = WeixinAccounts.getByOriginalId(w_user.account_original_id)
        user_info = weixin_account.db_account.get_user_info(w_user.openid)
        try:
            if not w_user.nickname:
                w_user.nickname = user_info.get('nickname', "")
                w_user.sex = user_info.get('sex', 0)
                w_user.city = user_info.get('city', "")
                w_user.country = user_info.get('country', "")
                w_user.headimgurl = user_info.get('headimgurl', "")
                w_user.unionid = user_info.get('unionid', "")
                w_user.province = user_info.get('province', "")
                w_user.subscribe = user_info.get('subscribe', 0)
                w_user.subscribe_time = user_info.get('subscribe_time', 0)
                w_user.nickname = filter_emoji( w_user.nickname, "*")
                w_user.save()
        except Exception, e:
            logger.debug(e.message)

        return Response(user_info)

class GenerateQRSceneTicket(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        original_id = request.GET.get('original_id')
        channel_code = request.GET.get('code')
        # phone = request.GET.get('phone')
        # if not original_id or not channel_code or not phone:
        if not original_id or not channel_code:
            return Response({'errcode':-1, 'errmsg':"-1"})
        # user_profile = WanglibaoUserProfile.objects.filter(phone=phone).first()
        # if not user_profile or user_profile.user_id != request.user.id:
        #     return Response({'errcode':-2, 'errmsg':"invalid phone"})
        weixin_account = WeixinAccounts.getByOriginalId(original_id)

        client = WeChatClient(weixin_account.app_id, weixin_account.app_secret, weixin_account.access_token)
        scene_id = str(request.user.id)

        channel = WeiXinChannel.objects.filter(code=channel_code).first()
        if channel:
            scene_id = scene_id + str(channel.digital_code)
            scene_id = int(scene_id)
            # print int(request.user.id)
            qrcode_data = {"action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": scene_id}}}
            # qrcode_data = {"action_name":"QR_LIMIT_SCENE", "action_info":{"scene": {"scene_id": phone}}}
            try:
                rs = client.qrcode.create(qrcode_data)
                qrcode_url = client.qrcode.get_url(rs.get('ticket'))
            except WeChatException,e:
                logger.debug("'errcode':%s, 'errmsg':%s"%(e.errcode, e.errmsg))
                return Response({'errcode':e.errcode, 'errmsg':e.errmsg, "qrcode_url":weixin_account.qrcode_url})
            return Response({'qrcode_url':qrcode_url})
        logger.debug("code does not exist")
        return Response({'errcode':-2, 'errmsg':"code does not exist", "qrcode_url":weixin_account.qrcode_url})


class GenerateQRLimitSceneTicket(APIView):
    permission_classes = ()
    def get(self, request):
        qrcode_id = request.GET.get('id')
        if not qrcode_id:
            return Response({'errcode':-1, 'errmsg':"-1"})
        qrcode = QrCode.objects.filter(id=qrcode_id).first()
        if not qrcode:
            return Response({'errcode':-2, 'errmsg':"-2"})
        if qrcode.ticket:
            return Response({'errcode':-3, 'errmsg':"-3"})
        weixin_account = WeixinAccounts.getByOriginalId(qrcode.account_original_id)
        client = WeChatClient(weixin_account.app_id, weixin_account.app_secret, weixin_account.access_token)
        qrcode_data = {"action_name":"QR_LIMIT_STR_SCENE", "action_info":{"scene": {"scene_str": qrcode.weiXinChannel.code}}}
        try:
            rs = client.qrcode.create(qrcode_data)
            qrcode.ticket = rs.get('ticket')
            qrcode.url = rs.get('url')
            qrcode.save()
        except Exception, e:
            print e
            return Response({'code': -1, 'message': 'error'})
        return Response(rs)


class WeixinCouponList(TemplateView):
    template_name = 'weixin_reward.jade'

    def get_context_data(self, **kwargs):

        status = kwargs['status']
        if status not in ('used', 'unused', 'expires'):
            status = 'unused'

        user = self.request.user
        result = backends.list_redpack(user, 'all', 'all', 0, 'all')
        packages = result['packages'].get(status, [])
        return {
            "packages": packages,
            "status": status
        }


def testTemplate():
    a = MessageTemplate('_8E2B4QZQC3yyvkubjpR6NYXtUXRB9Ya79MYmpVvQ1o',
                        first=u"您好，恭喜您账户绑定成功！\n  \n您的账户已经与微信账户绑定在一起。",
                        keyword1=u"2015年09月22日")


def checkAndSendProductTemplate(sender, **kw):
    # print kw
    product = kw["instance"]


    matches = re.search(u'日计息', product.pay_method)
    period = product.period
    period_desc = "%s个月"%product.period
    if matches and matches.group():
        period = period/30.0   # 天
        period_desc = '%s天'%product.period
    if product.activity:
        rate_desc = "%s%% + %s%%"%(product.expected_earning_rate, float(Decimal(str(product.activity.rule.rule_amount)).quantize(Decimal('0.000'), 'ROUND_DOWN')) * 100)
    else:
        rate_desc = "%s%%"%product.expected_earning_rate

    services = SubscribeService.objects.filter(channel='weixin', is_open=True, type=0).all()
    for service in services:
        if period == service.num_limit:
            sub_records = SubscribeRecord.objects.filter(service=service).all()
            for sub_record in sub_records:
                if sub_record.w_user and sub_record.w_user.subscribe==1 and sub_record.w_user.user:
                        url = settings.CALLBACK_HOST + '/weixin/view/detail/%s/'%product.id
                        template = MessageTemplate(PRODUCT_ONLINE_TEMPLATE_ID,
                            first=service.describe, keyword1=product.name, keyword2=rate_desc,
                            keyword3=period_desc, keyword4=product.pay_method, url=url)
                        sendTemplate(sub_record.w_user, template)




def checkProduct(sender, **kw):
    product = kw["instance"]
    if getattr(product, "old_status", ""):
        if product.old_status == u'待审核' and product.status==u'正在招标':
            publish_time = product.publish_time
            utc_now = timezone.now()
            if utc_now <= publish_time:
                exec_time = publish_time + datetime.timedelta(minutes=1)
                detect_product_biding.apply_async(kwargs={
                   "product_id":product.id
                },
                                                  eta= exec_time,
                                                  queue='celery01')
            else:
                exec_time = utc_now + datetime.timedelta(minutes=1)
                detect_product_biding.apply_async(kwargs={
                   "product_id":product.id
                },
                                                  eta=exec_time,
                                                  queue='celery01')

def recordProduct(sender, **kw):
    try:
        product = kw["instance"]
        if product.status == u'正在招标':
            db_product = P2PProduct.objects.get(pk=product.id)
            setattr(product, 'old_status', db_product.status)
    except:
        pass

pre_save.connect(recordProduct, sender=P2PProduct, dispatch_uid="product-pre-save-signal")
post_save.connect(checkProduct, sender=P2PProduct, dispatch_uid="product-post-save-signal")


class WeiXinReceivedAll(TemplateView):
    """ 回款计划所有 """
    template_name = 'weixin_received_all.jade'
class WeiXinReceivedMonth(TemplateView):
    """ 回款计划月 """
    template_name = 'weixin_received_month.jade'
class WeiXinReceivedDetail(TemplateView):
    """ 回款计划详细 """
    template_name = 'weixin_received_detail.jade'
