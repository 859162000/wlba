# encoding:utf-8
from django.views.generic import View, TemplateView, RedirectView
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login
from django.template import Template, Context
from django.template.loader import get_template
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response

from wanglibao_account.forms import EmailOrPhoneAuthenticationForm
from wanglibao_account.forms import LoginAuthenticationNoCaptchaForm
from wanglibao_buy.models import FundHoldInfo
from wanglibao_banner.models import Banner
from wanglibao_p2p.models import P2PEquity
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_redpack import backends
from wanglibao_rest import utils
from django.contrib.auth.models import User
from constant import MessageTemplate
from constant import (ACCOUNT_INFO_TEMPLATE_ID, BIND_SUCCESS_TEMPLATE_ID, UNBIND_SUCCESS_TEMPLATE_ID)
from weixin.util import getAccountInfo
from wanglibao_profile.models import WanglibaoUserProfile


from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from wanglibao_pay.models import Bank
from wechatpy import parse_message, create_reply, WeChatClient
from wechatpy.replies import TransferCustomerServiceReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException, WeChatException
from wechatpy.oauth import WeChatOAuth
from weixin.common.decorators import weixin_api_error
from weixin.common.wx import generate_js_wxpay
from .models import Account, WeixinUser, WeixinAccounts, AuthorizeInfo, QrCode, SubscribeService, SubscribeRecord
from .common.wechat import tuling
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
from wechatpy.parser import parse_message
from wechatpy.messages import BaseMessage, TextMessage
import datetime, time
from wechatpy.events import (BaseEvent, ClickEvent, SubscribeScanEvent, ScanEvent, UnsubscribeEvent, SubscribeEvent,\
                             TemplateSendJobFinishEvent)
from rest_framework import renderers
import functools

def checkBindDeco(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        toUserName = self.msg._data['ToUserName']
        fromUserName = self.msg._data['FromUserName']
        account = Account.objects.get(original_id=toUserName)
        w_user = getOrCreateWeixinUser(fromUserName, account)
        check_bind = False
        if isinstance(self.msg, BaseEvent):
            if isinstance(self.msg,(ClickEvent,)):
                if self.msg.key == 'test_hmm' or self.msg.key == 'my_account':
                    check_bind = True
        elif isinstance(self.msg, BaseMessage):
            content = self.msg.content.lower()
            sub_service = SubscribeService.objects.filter(channel='weixin', is_open=True, key=content).first()
            if content == 'td' or sub_service:
                check_bind = True

        if check_bind and not w_user.user:
            txt = self.getBindTxt(fromUserName, account.id)
            reply = create_reply(txt, self.msg)
            return reply
        else:
            return func(self, *args, **kwargs)
    return wrapper

class WeixinJoinView(View):
    account = None

    def check_signature(self, request, account_key):
        account = Account.objects.get(pk=account_key)#WeixinAccounts.get(account_key)
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
        print msg
        reply = None
        toUserName = msg._data['ToUserName']
        print "toUserName:::",toUserName
        fromUserName = msg._data['FromUserName']
        createTime = msg._data['CreateTime']
        weixin_account = WeixinAccounts.getByOriginalId(toUserName)
        account = weixin_account.db_account
        if isinstance(msg, BaseEvent):
            if isinstance(msg, ClickEvent):
                reply = self.process_click_event(msg)
            elif isinstance(msg, SubscribeEvent):
                reply = self.process_subscribe(msg, toUserName)
            elif isinstance(msg, UnsubscribeEvent):
                w_user = getOrCreateWeixinUser(fromUserName, account)
                if w_user.subscribe != 0:
                    w_user.subscribe = 0
                    w_user.save()
                reply = create_reply(u'欢迎下次关注我们！', msg)
            elif isinstance(msg, SubscribeScanEvent):
                reply = self.process_subscribe(msg, toUserName)
            elif isinstance(msg, ScanEvent):
                w_user = getOrCreateWeixinUser(fromUserName, account)
                eventKey = msg._data['EventKey']
                #如果eventkey为用户id则进行绑定
                reply = self.process_subscribe(msg, toUserName)
            elif isinstance(msg, TemplateSendJobFinishEvent):
                pass
        elif isinstance(msg, BaseMessage):
            if isinstance(msg, TextMessage):
                reply = self.check_service_subscribe(msg, account)
                # 自动回复  5000次／天
                if not reply:
                    reply = tuling(msg)
                if not reply:
                    # 多客服转接
                    reply = TransferCustomerServiceReply(message=msg)
            # else:
            #     reply = create_reply(u'更多功能，敬请期待！', msg)
        if reply == -1:
            return HttpResponse("")
        if not reply:
            reply = create_reply(u'这个是不是不需要回复什么的?', msg)
        return HttpResponse(reply.render())


    @checkBindDeco
    def process_click_event(self, msg):
        reply = None
        sub_services = SubscribeService.objects.filter(channel='weixin', is_open=True).all()
        toUserName = msg._data['ToUserName']
        fromUserName = msg._data['FromUserName']
        account = WeixinAccounts.getByOriginalId(toUserName)
        w_user = getOrCreateWeixinUser(fromUserName, account.db_account)
        if msg.key == 'subscribe_service':
            txt = u'客官，请回复相关数字订阅最新项目通知，系统会在第一时间发送给您相关信息。\n'
            for sub_service in sub_services:
                txt += (sub_service.describe + '\n')
            txt += u'如需退订请回复TD'
            reply = create_reply(txt, msg)
        if msg.key == 'bind_weixin':
            if not w_user.user:
                txt = self.getBindTxt(fromUserName)
            else:
                txt = self.getUnBindTxt(fromUserName, w_user.user.wanglibaouserprofile.phone)
            reply = create_reply(txt, msg)
        if msg.key == 'my_account':
            account_info = getAccountInfo(w_user.user)
            # 【账户概况】
            # 总资产       (元）： 12000.00
            # 可用余额（元）： 108.00
            # 累计收益（元）：  79.00
            # 待收收益（元）：  24.00
            a = MessageTemplate(ACCOUNT_INFO_TEMPLATE_ID,
                    keyword1=account_info['total_asset'],
                    keyword2=account_info['p2p_margin'], keyword3=account_info['p2p_total_paid_interest'],
                    keyword4=account_info['p2p_total_unpaid_interest'])
            SendTemplateMessage.sendTemplate(w_user, a)
            reply = -1
        return reply

    @checkBindDeco
    def check_service_subscribe(self, msg, account):
        fromUserName = msg._data['FromUserName']
        w_user = getOrCreateWeixinUser(fromUserName, account)
        content = msg.content.lower()
        reply = None
        txt = None
        if content == 'td':
            sub_records = SubscribeRecord.objects.filter(user=w_user.user, status=True)
            if sub_records.exists():
                sub_records.update(status=False)
                txt = u'订阅项目已退订成功，如需订阅相关项目，请再次点击【个性化项目】进行订阅'
            else:
                txt = u'您没有可退订项目，如需订阅相关项目，请再次点击【个性化项目】进行订阅'
            reply = create_reply(txt, msg)
            return reply
        sub_service = SubscribeService.objects.filter(channel='weixin', is_open=True, key=content).first()
        if sub_service:
            sub_service_record = SubscribeRecord.objects.filter(user=w_user.user, service = sub_service).first()
            if sub_service_record and sub_service_record.status==1:
                txt = u'客官真健忘，您已经订阅此项目通知，订阅其他上线通知项目吧～'
            if not sub_service_record:
                sub_service_record = SubscribeRecord()
                sub_service_record.service = sub_service
                sub_service_record.user = w_user.user
            if not sub_service_record.status:
                sub_service_record.status = True
                sub_service_record.save()
                txt = u'恭喜您，%s订阅成功，系统会在第一时间发送给您相关信息'%(sub_service.describe)
            if txt:
                reply = create_reply(txt, msg)
        return reply


    def process_subscribe(self, msg, original_id):
        fromUserName = msg._data['FromUserName']
        eventKey = msg._data['EventKey']
        account = WeixinAccounts.getByOriginalId(original_id)
        w_user = getOrCreateWeixinUser(fromUserName, account.db_account)
        reply = None
        if w_user.subscribe != 1:
            w_user.subscribe = 1
            w_user.save()

        #如果eventkey为用户id则进行绑定
        if eventKey and eventKey.isdigit():
            userProfile = WanglibaoUserProfile.objects.filter(phone=eventKey).first()
            if userProfile:
                rs, txt = bindUser(w_user, userProfile.user)
                reply = create_reply(txt, msg)
        else:
            if not w_user.scene_id:
                w_user.scene_id = eventKey
                w_user.save()
        if not reply and not w_user.user:
            txt = self.getBindTxt(fromUserName)
            reply = create_reply(txt, msg)
        if not reply:
            articles = self.getSubscribeArticle()
            reply = create_reply(articles, msg)
        return reply

    def getSubscribeArticle(self):
        image = "http://e.hiphotos.baidu.com/baike/c0%3Dbaike80%2C5%2C5%2C80%2C26/sign=410619fb3d01213fdb3e468e358e5db4/9f510fb30f2442a71525d087d543ad4bd11302ec.jpg"
        url = 'https://www.wanglibao.com/activity/new_user/'
        description = '大数据下的网利宝'
        title = '大数据下的网利宝'
        image1 = "http://e.hiphotos.baidu.com/baike/c0%3Dbaike80%2C5%2C5%2C80%2C26/sign=410619fb3d01213fdb3e468e358e5db4/9f510fb30f2442a71525d087d543ad4bd11302ec.jpg"
        url1 = 'https://www.wanglibao.com/milestone/'
        description1 = '网利宝大事记'
        title1 = '网利宝大事记'
        return [{'image':image, 'url':url, 'description':description, 'title':title},
                {'image':image1, 'url':url1, 'description':description1, 'title':title1}]

    def getBindTxt(self, fromUserName):
        bind_url = settings.WEIXIN_CALLBACK_URL + reverse('weixin_bind') + "?openid=%s"%(fromUserName)
        txt = u"终于等到你，还好我没放弃。绑定网利宝帐号，轻松投资、随时随地查看收益！<a href='%s'>【立即绑定】</a>"%(bind_url)
        return txt

    def getUnBindTxt(self, fromUserName, userPhone):
        unbind_url = settings.WEIXIN_CALLBACK_URL + reverse('weixin_unbind') + "?openid=%s"%(fromUserName)
        txt = u"您的微信绑定帐号为：%s\n"%userPhone\
            +u"如需解绑当前帐号，请点击<a href='%s'>【立即解绑】</a>"%unbind_url
        return txt


    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WeixinJoinView, self).dispatch(request, *args, **kwargs)



def getOrCreateWeixinUser(openid, account):
    w_user = WeixinUser.objects.filter(openid=openid).first()
    if w_user.account_original_id != account.original_id:
        w_user.account_original_id = account.original_id
        w_user.save()
    if not w_user:
        w_user = WeixinUser()
        w_user.openid = openid
        w_user.account_original_id = account.original_id
        w_user.save()
    if not w_user.nickname:
        try:
            user_info = account.get_user_info(openid)
            w_user.nickname = user_info.get('nickname', "")
            w_user.sex = user_info.get('sex')
            w_user.city = user_info.get('city', "")
            w_user.country = user_info.get('country', "")
            w_user.headimgurl = user_info.get('headimgurl', "")
            w_user.unionid =  user_info.get('unionid', '')
            w_user.province = user_info.get('province', '')
            w_user.subscribe = user_info.get('subscribe', '')
            # if not w_user.subscribe_time:
            w_user.subscribe_time = user_info.get('subscribe_time', '')
            w_user.save()
        except WeChatException, e:
            pass
    return w_user


def bindUser(w_user, user):
    if w_user.user:
        if w_user.user.id==user.id:
            return 1, u'你已经绑定, 请勿重复绑定'
        return 2, u'你微信已经绑定%s'%w_user.user.wanglibaouserprofile.phone
    other_w_user = WeixinUser.objects.filter(user=user).first()
    if other_w_user:
        return 3, u'你的手机号%s已经绑定微信%s,请绑定其他网利宝帐号'%(user.wanglibaouserprofile.phone, other_w_user.nickname)
    w_user.user = user
    w_user.save()
    return 0, u'绑定成功'

class WeixinLogin(TemplateView):
    template_name = 'weixin_login_new.jade'

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
        return {
            'context': context,
            'next': next
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

class SendTemplateMessage(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    BIND_SUCCESS = "bind_success"

    @classmethod
    def sendTemplate(cls, weixin_user, message_template):
        weixin_account = WeixinAccounts.getByOriginalId(weixin_user.account_original_id)
        account = weixin_account.db_account
        # account = Account.objects.get(original_id=weixin_user.account_original_id)
        client = WeChatClient(account.app_id, account.app_secret)
        client.message.send_template(weixin_user.openid, template_id=message_template.template_id,
                                     top_color=message_template.top_color, data=message_template.data,
                                     url=message_template.url)
    def post(self, request):
        openid = request.POST.get('openid')
        if not openid:
            return Response({'error':-1})
        w_user = WeixinUser.objects.filter(openid=openid).first()
        template_type = request.POST.get('template_type', '')
        template = None
        if template_type.lower() == SendTemplateMessage.BIND_SUCCESS and w_user.user == request.user:
            now_str = datetime.datetime.now().strftime('%Y年%m月%d日')
            template = MessageTemplate(BIND_SUCCESS_TEMPLATE_ID, first=u"账户绑定通知", name1="",
                    name2=now_str)
        if template:
            SendTemplateMessage.sendTemplate(w_user, template)
        return Response({'message':'ok'})


class JumpPageTemplate(TemplateView):
    template_name = 'sub_times.jade'

    def get_context_data(self, **kwargs):
        context = super(JumpPageTemplate, self).get_context_data(**kwargs)
        message = self.request.GET.get('message', 'ERROR')
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
            if rs == 0:
                now_str = datetime.datetime.now().strftime('%Y年%m月%d日')
                template = MessageTemplate(BIND_SUCCESS_TEMPLATE_ID,
                     name2=user.wanglibaouserprofile.phone, time=now_str)
                SendTemplateMessage.sendTemplate(weixin_user, template)
        except WeixinUser.DoesNotExist:
            pass
        context['message'] = txt
        return {
            'context': context,
            'next': next
            }

def redirectToJumpPage(message):
    url = reverse('jump_page')+'?message=%s'%message
    return HttpResponseRedirect(url)

class UnBindWeiUser(TemplateView):
    template_name = 'sub_is_bind.jade'

    def get_context_data(self, **kwargs):
        context = super(UnBindWeiUser, self).get_context_data(**kwargs)
        openid = self.request.GET.get('openid', '')
        context['openid'] = openid
        next = self.request.GET.get('next', '')
        return {
            'context': context,
            'next': next
            }

    def dispatch(self, request, *args, **kwargs):
        openid = self.request.GET.get('openid', '')
        if not openid:
            return redirectToJumpPage("error:-1")
        w_user = WeixinUser.objects.filter(openid=openid).first()
        if not w_user:
            message = u"请从[服务中心]点击[绑定微信]进行绑定"
            return redirectToJumpPage(message)
        if not w_user.user:
            message = u"您没有绑定的网利宝帐号"
            return redirectToJumpPage(message)
        return super(UnBindWeiUser, self).dispatch(request, *args, **kwargs)

class UnBindWeiUserAPI(APIView):
    permission_classes = ()
    http_method_names = ['post']

    def post(self, request):
        openid = request.POST.get('openid')
        weixin_user = WeixinUser.objects.get(openid=openid)
        if weixin_user.user:
            user_phone = weixin_user.user.wanglibaouserprofile.phone
            weixin_user.user = None
            weixin_user.save()
            now_str = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')
            template = MessageTemplate(UNBIND_SUCCESS_TEMPLATE_ID, keyword1=user_phone, keyword2=now_str)
            SendTemplateMessage.sendTemplate(weixin_user, template)

        return Response({'message':'ok'})


class WeixinJsapiConfig(APIView):
    permission_classes = ()
    http_method_names = ['get']

    @weixin_api_error
    def get(self, request):
        if settings.ENV == settings.ENV_DEV:
            request.session['account_key'] = 'test'
            account = WeixinAccounts.get('test')
        else:
            request.session['account_key'] = 'sub_1'
            account = WeixinAccounts.get('sub_1')

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

        banner = Banner.objects.filter(device='weixin', type='banner', is_used=True).order_by('-priority')

        return {
            'results': p2p_products[:10],
            'banner': banner,
        }


def _generate_ajax_template(content, template_name=None):

    context = Context({
        'results': content,
    })

    if template_name:
        template = get_template(template_name)
    else:
        template = Template('<div></div>')

    return template.render(context)


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

    def get_template_names(self):
        template = self.kwargs['template']
        if template == 'calculator':
            template_name = 'weixin_calculator.jade'
        elif template == 'buy':
            template_name = 'weixin_buy.jade'
        else:
            template_name = 'weixin_detail.jade'

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
        if user.is_authenticated():
            user_margin = user.margin.margin
            equity_record = P2PEquity.objects.filter(product=p2p['id']).filter(user=user).first()
            if equity_record is not None:
                current_equity = equity_record.equity

            device = utils.split_ua(self.request)
            result = backends.list_redpack(user, 'available', device['device_type'], p2p['id'])
            redpacks = result['packages'].get('available', [])

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
        p2p_activity_interest = 0
        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal  # 待收本金
                p2p_total_paid_interest += equity.pre_paid_interest  # 累积收益
                p2p_total_unpaid_interest += equity.unpaid_interest  # 待收益
                p2p_total_interest += equity.pre_total_interest  # 总收益
                p2p_activity_interest += equity.activity_interest  # 活动收益

        p2p_margin = user.margin.margin  # P2P余额
        p2p_freeze = user.margin.freeze  # P2P投资中冻结金额
        p2p_withdrawing = user.margin.withdrawing  # P2P提现中冻结金额
        p2p_unpayed_principle = unpayed_principle  # P2P待收本金

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
            'p2p_total_unpaid_interest': p2p_total_unpaid_interest,  # p2p总待收益
            'p2p_total_paid_interest': p2p_total_paid_interest + p2p_activity_interest,  # P2P总累积收益
            'p2p_total_interest': p2p_total_interest,  # P2P总收益
            'banner': banner,
        }


class WeixinRecharge(TemplateView):
    template_name = 'weixin_recharge.jade'

    def get_context_data(self, **kwargs):

        banks = Bank.get_kuai_deposit_banks()
        next = self.request.GET.get('rechargeNext', '')
        return {
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

    def get_template_names(self):
        status = self.kwargs['status']
        if status == 'buying':
            template_name = 'weixin_transaction_buying.jade'
        elif status == 'finished':
            template_name = 'weixin_transaction_finished.jade'
        else:
            template_name = 'weixin_transaction.jade'

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
        p2p_cards = Card.objects.filter(user__exact=self.request.user).count()
        return {
            'p2p_cards': p2p_cards,
        }


class WeixinAccountBankCard(TemplateView):
    template_name = 'weixin_bankcard.jade'

    def get_context_data(self, **kwargs):
        p2p_cards = Card.objects.filter(user__exact=self.request.user)
        return {
            'p2p_cards': p2p_cards,
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
        try:
            account = Account.objects.get(original_id=account_id)
        except Account.DoesNotExist:
            try:
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
        if auth and auth=='1':
            oauth = WeChatOAuth(account.app_id, account.app_secret, redirect_uri=redirect_uri, scope='snsapi_userinfo', state=account_id)
        else:
            oauth = WeChatOAuth(account.app_id, account.app_secret, redirect_uri=redirect_uri, state=account_id)
        print oauth.authorize_url
        return redirect(oauth.authorize_url)


class AuthorizeUser(APIView):
    permission_classes = ()
    def get(self, request):
        account_id = self.request.GET.get('state')
        try:
            account = Account.objects.get(original_id=account_id)
        except Account.DoesNotExist:
            try:
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
            w_user = WeixinUser.objects.filter(openid=openid).first()
            save_user = False

            if not w_user:
                w_user = WeixinUser()
                w_user.account_original_id = account.original_id
                w_user.openid = openid
                save_user = True

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

            appendkeys = []
            for key in request.GET.keys():
                if key == u'state' or key == u'code':
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
        account = weixin_account.db_account
        try:
            oauth = WeChatOAuth(account.app_id, account.app_secret, )
            if not w_user.auth_info.check_access_token():
                res = oauth.refresh_access_token(w_user.auth_info.refresh_token)
                w_user.auth_info.access_token = res['access_token']
                w_user.auth_info.refresh_token = res['refresh_token']
                w_user.auth_info.access_token_expires_at = Account._now() + datetime.timedelta(seconds=res.get('expires_in') - 60)
                w_user.auth_info.save()
            user_info = oauth.get_user_info(w_user.openid, w_user.auth_info.access_token)
            w_user.nickname = user_info.get('nickname', "")
            w_user.sex = user_info.get('sex')
            w_user.city = user_info.get('city', "")
            w_user.country = user_info.get('country', "")
            w_user.headimgurl = user_info.get('headimgurl', "")
            w_user.unionid =  user_info.get('unionid', '')
            w_user.province = user_info.get('province', '')
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
        account = weixin_account.db_account
        user_info = account.get_user_info(w_user.openid)
        if not w_user.nickname:
            w_user.nickname = user_info.get('nickname', "")
            w_user.sex = user_info.get('sex')
            w_user.city = user_info.get('city', "")
            w_user.country = user_info.get('country', "")
            w_user.headimgurl = user_info.get('headimgurl', "")
            w_user.unionid = user_info.get('unionid', '')
            w_user.province = user_info.get('province', '')
            w_user.subscribe = user_info.get('subscribe', '')
            w_user.subscribe_time = user_info.get('subscribe_time', '')
            w_user.save()
        return Response(user_info)

class GenerateQRSceneTicket(APIView):
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
        account = Account.objects.get(original_id=qrcode.account_original_id)
        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        qrcode_data = {"action_name":"QR_LIMIT_STR_SCENE", "action_info":{"scene": {"scene_str": qrcode.scene_str}}}
        try:
            rs = client.qrcode.create(qrcode_data)
            qrcode.ticket = rs.get('ticket')
            qrcode.url = rs.get('url')
            qrcode.save()
        except Exception,e:
            print e
            return Response({'code':-1, 'message':'error'})
        return Response(rs)

class GenerateQRLimitSceneTicket(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        original_id = request.POST.get('original_id')
        if not original_id:
            return Response({'errcode':-1, 'errmsg':"-1"})
        # account = Account.objects.get(original_id=original_id)
        weixin_account = WeixinAccounts.getByOriginalId(original_id)
        account = weixin_account.db_account
        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        qrcode_data = {"action_name": "QR_LIMIT_STR_SCENE", "action_info": {"scene": {"scene_str": str(request.user.wanglibaouserprofile.phone)}}}
        # qrcode_data = {"action_name":"QR_LIMIT_SCENE", "action_info":{"scene": {"scene_id": phone}}}
        try:
            rs = client.qrcode.create(qrcode_data)
            qrcode_url = client.qrcode.get_url(rs.get('ticket'))
        except WeChatException,e:
            return Response({'errcode':e.errcode, 'errmsg':e.errmsg})
        return Response({'qrcode_url':qrcode_url})

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

# class WeixinBindLogin(TemplateView):
#     template_name = 'sub_login.jade'
#
#     def get_context_data(self, **kwargs):
#         context = super(WeixinBindLogin, self).get_context_data(**kwargs)
#         openid = self.request.GET.get('openid', '')
#         context['openid'] = openid
#         next = self.request.GET.get('next', '')
#         return {
#             'context': context,
#             'next': next
#             }
#
#     def dispatch(self, request, *args, **kwargs):
#         openid = self.request.GET.get('openid', '')
#         if not openid:
#             return redirectToJumpPage("error:-1")
#         w_user = WeixinUser.objects.filter(openid=openid).first()
#         if not w_user:
#             message = u"请从[服务中心]点击[绑定微信]进行绑定"
#             return redirectToJumpPage(message)
#         if w_user.user:
#             message = u'你微信已经绑定%s'%w_user.user.wanglibaouserprofile.phone
#             return redirectToJumpPage(message)
#         return super(WeixinBindLogin, self).dispatch(request, *args, **kwargs)
#
# class WeixinBindRegister(WeixinRegister):
#     template_name = 'sub_regist.jade'
#
#     def get_context_data(self, **kwargs):
#         context = super(WeixinBindRegister, self).get_context_data(**kwargs)
#         openid = self.request.GET.get('openid', '')
#         context['openid'] = openid
#         return context
#
#     def dispatch(self, request, *args, **kwargs):
#         openid = self.request.GET.get('openid', '')
#         if not openid:
#             return redirectToJumpPage("error:-1")
#         w_user = WeixinUser.objects.filter(openid=openid).first()
#         if not w_user:
#             message = u"请从[服务中心]点击[绑定微信]进行绑定"
#             return redirectToJumpPage(message)
#         if w_user.user:
#             message = u'你微信已经绑定网利宝账户%s'%w_user.user.wanglibaouserprofile.phone
#             return redirectToJumpPage(message)
#         return super(WeixinBindRegister, self).dispatch(request, *args, **kwargs)
