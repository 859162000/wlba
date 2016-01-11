#!/usr/bin/env python
# encoding:utf-8

import json
import logging
from datetime import timedelta, datetime, time

import re
from django.db.models import Count, Sum, F
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from rest_framework import generics, renderers
from django.http import HttpResponse
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from marketing.models import PromotionToken, Channels, IntroducedBy
from marketing.utils import set_promo_user, get_channel_record
from wanglibao_account.cooperation import CoopRegister
# from wanglibao_account.cooperation import save_to_binding
from wanglibao_redpack.models import RedPackEvent
from random import randint
from wanglibao_sms.tasks import send_messages
from wanglibao_account.utils import create_user
from wanglibao_activity.models import ActivityRecord, Activity, ActivityRule
from wanglibao_portfolio.models import UserPortfolio
from wanglibao_portfolio.serializers import UserPortfolioSerializer
from wanglibao_rest.serializers import AuthTokenSerializer
from wanglibao_sms.utils import send_validation_code, validate_validation_code, send_rand_pass, generate_validate_code
from wanglibao_sms.models import PhoneValidateCode
from wanglibao.const import ErrorNumber
from wanglibao_redpack import backends as redpack_backends
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_account.models import VerifyCounter, UserPushId
from wanglibao_p2p.models import P2PRecord, ProductAmortization, P2PProduct
from wanglibao_account.utils import verify_id, detect_identifier_type
from wanglibao_sms import messages, backends
from django.utils import timezone
# from wanglibao_account import message as inside_message
from misc.models import Misc
from wanglibao_account.forms import IdVerificationForm, verify_captcha
# from marketing.helper import RewardStrategy, which_channel, Channel
from wanglibao_rest.utils import split_ua, get_client_ip
from django.http import HttpResponseRedirect
from wanglibao.templatetags.formatters import safe_phone_str, safe_phone_str1
from marketing.tops import Top
from marketing import tools
from marketing.models import PromotionToken
from marketing.utils import local_to_utc
from django.conf import settings
from wanglibao_account.models import Binding
from wanglibao_anti.anti.anti import AntiForAllClient
from wanglibao_redpack.models import Income
from decimal import Decimal
from wanglibao_reward.models import WanglibaoUserGift, WanglibaoActivityGift
from common import DecryptParmsAPIView
import requests
from weixin.models import WeixinUser
from weixin.util import bindUser


logger = logging.getLogger('wanglibao_rest')


class UserPortfolioView(generics.ListCreateAPIView):
    queryset = UserPortfolio.objects.all()
    serializer_class = UserPortfolioSerializer

    def get_queryset(self):
        user_pk = self.kwargs['user_pk']
        return self.queryset.filter(user_id=user_pk)


class CaptchaValidationCodeView(APIView):
    """ 单独验证验证码 """
    permission_classes = ()

    def post(self, request, phone):
        phone_number = phone.strip()
        phone_check = WanglibaoUserProfile.objects.filter(phone=phone_number)
        if phone_check:
            return Response({"message": u"该手机号已经被注册，不能重复注册",
                            "error_number": ErrorNumber.duplicate,
                            "type":"exists"}, status=400)

        res, message = verify_captcha(dic=request.POST, keep=True)
        if not res:
            return Response({'message': message, "type": "captcha"}, status=403)

        return Response({'message': '验证码正确'}, status=200)


class SendValidationCodeView(APIView):
    """
    The phone validate view which accept a post request and send a validate code to the phone
    """
    permission_classes = ()
    #throttle_classes = (UserRateThrottle,)

    def post(self, request, phone):
        """
            modified by: Yihen@20150812
            descrpition: if...else(line98~line101)的修改，增强验证码后台处理，防止被刷单
        """
        phone_number = phone.strip()
        if not AntiForAllClient(request).anti_special_channel():
            res, message = False, u"请输入验证码"
        else:
            res, message = verify_captcha(request.POST)

        if not res:
            return Response({'message': message, "type":"captcha"}, status=403)

        status, message = send_validation_code(phone_number, ip=get_client_ip(request))
        return Response({
                            'message': message
                        }, status=status)


class TestSendRegisterValidationCodeView(APIView):
    permission_classes = ()

    def post(self, request, phone):
        phone = phone.strip()
        user = WanglibaoUserProfile.objects.filter(phone=phone).first()
        if user:
            return Response({"ret_code":-1, "message":"手机号已经注册"})

        phone_validate_code_item = PhoneValidateCode.objects.filter(phone=phone).first()

        if phone_validate_code_item:
            phone_validate_code_item.code_send_count += 1
        else:
            phone_validate_code_item = PhoneValidateCode()
            phone_validate_code_item.phone = phone
        phone_validate_code_item.validate_code = generate_validate_code()
        phone_validate_code_item.last_send_time = timezone.now()
        phone_validate_code_item.is_validated = False
        phone_validate_code_item.save()
        return Response({"ret_code":0, "message":"ok", "vcode":phone_validate_code_item.validate_code})

class SendRegisterValidationCodeView(APIView):
    """
    The phone validate view which accept a post request and send a validate code to the phone
    """
    permission_classes = ()
    # throttle_classes = (UserRateThrottle,)

    def post(self, request, phone):
        """
            modified by: Yihen@20150812
            descrpition: if...else(line153~line156)的修改，增强验证码后台处理，防止被刷单
        """
        phone_number = phone.strip()
        phone_check = WanglibaoUserProfile.objects.filter(phone=phone_number)
        if phone_check:
            return Response({"message": u"该手机号已经被注册，不能重复注册", 
                            "error_number": ErrorNumber.duplicate,
                            "type":"exists"}, status=400)

        if not AntiForAllClient(request).anti_special_channel():
            res, message = False, u"请输入验证码"
        else:
            res, message = verify_captcha(request.POST)

        if not res:
            return Response({'message': message, "type":"captcha"}, status=403)

        status, message = send_validation_code(phone_number, ip=get_client_ip(request))
        return Response({'message': message, "type":"validation"}, status=status)

    def dispatch(self, request, *args, **kwargs):
        return super(SendRegisterValidationCodeView, self).dispatch(request, *args, **kwargs)

class WeixinSendRegisterValidationCodeView(APIView):
    """
    The phone validate view which accept a post request and send a validate code to the phone

    在iphone5 iphone5s中 原接口返回430错误 重写复制 SendRegisterValidationCodeView 类
    添加 throttle_classes = (UserRateThrottle,)
    删除 dispatch 方法

    只提供给微信端注册的手机验证码接口使用
    """
    permission_classes = ()
    throttle_classes = (UserRateThrottle,)

    def post(self, request, phone, format=None):
        phone_number = phone.strip()
        #phone_check = WanglibaoUserProfile.objects.filter(phone=phone_number, phone_verified=True)
        phone_check = WanglibaoUserProfile.objects.filter(phone=phone_number)
        if phone_check:
            return Response({
                                "message": u"该手机号已经被注册，不能重复注册",
                                "error_number": ErrorNumber.duplicate
                            }, status=400)

        #phone_validate_code_item = PhoneValidateCode.objects.filter(phone=phone_number).first()
        #if phone_validate_code_item:
        #    count = phone_validate_code_item.code_send_count
        #    if count > 6:
        #        return Response({
        #                            "message": u"该手机号验证次数过于频繁，请联系客服人工注册",
        #                            "error_number": ErrorNumber.duplicate
        #                        }, status=400)

        status, message = send_validation_code(phone_number, ip=get_client_ip(request))
        return Response({
                            'message': message
                        }, status=status)



class RegisterAPIView(DecryptParmsAPIView):
    permission_classes = ()

    def generate_random_password(self, length):
        if length < 0:
            raise Exception("生成随机密码的长度有误")

        random_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        password = ""
        index = 0
        while index < length:
                password += str(random_list[randint(0,len(random_list)-1)])
                index += 1
        return password

    def post(self, request, *args, **kwargs):
        """ 
            modified by: Yihen@20150812
            descrpition: if(line282~line283)的修改，针对特定的渠道延迟返积分、发红包等行为，防止被刷单
        """
        identifier = self.params.get('identifier', "")
        password = self.params.get('password', "")
        validate_code = self.params.get('validate_code', "")
        # identifier = request.DATA.get('identifier', "")
        # password = request.DATA.get('password', "")
        # validate_code = request.DATA.get('validate_code', "")
        channel = request.session.get(settings.PROMO_TOKEN_QUERY_STRING, "")

        identifier = identifier.strip()
        password = password.strip()
        validate_code = validate_code.strip()
        if request.DATA.get('IGNORE_PWD', '') and not password:
            password = self.generate_random_password(6)
            logger.debug('系统为用户 %s 生成的随机密码是：%s' % (identifier, password))

        if not identifier or not password or not validate_code:
            return Response({"ret_code": 30011, "message": "信息输入不完整"})

        if not 6 <= len(password) <= 20:
            return Response({"ret_code": 30012, "message": u"密码需要在6-20位之间"})

        identifier_type = detect_identifier_type(identifier)
        if identifier_type != 'phone':
            return Response({"ret_code": 30013, "message": u"手机号输入错误"})

        status, message = validate_validation_code(identifier, validate_code)
        if status != 200:
            return Response({"ret_code": 30014, "message": message, "status":status })

        if User.objects.filter(wanglibaouserprofile__phone=identifier).first():
            return Response({"ret_code": 30015, "message": u"该手机号已经注册"})

        device = split_ua(request)
        invite_code = request.DATA.get('invite_code', "")

        #if not invite_code and "channel_id" in device:
        #    if device['channel_id'] == "baidu":
        #        invite_code = "baidushouji"
        #    elif device['channel_id'] == "mi":
        #        invite_code = "mi"
        #    else:
        #        invite_code = ""
                #invite_code = device['channel_id']
        #if not invite_code and ("channel_id" in device and device['channel_id'] == "baidu"):
        #    invite_code = "baidushouji"

        
        # Modify by hb on 2015-09-21
        if not invite_code or invite_code==u'weixin':
            invite_phone = request.DATA.get('invite_phone', "")
            if invite_phone:
                invite_code = PromotionToken.objects.filter(user__wanglibaouserprofile__phone=invite_phone).first()
                logger.error("invite_phone=[%s], invite_code=[%s]" % (invite_phone, invite_code))
            if not invite_code:
                invite_code = request.session.get(settings.PROMO_TOKEN_QUERY_STRING, None)
           
        if invite_code:
            try:
                record = get_channel_record(invite_code)
                if not record:
                    p = PromotionToken.objects.filter(token=invite_code).first()
                    if not p:
                        raise
            except:
                return Response({"ret_code": 30016, "message": "邀请码错误"})
 
        user = create_user(identifier, password, "")
        if not user:
            return Response({"ret_code": 30014, "message": u"注册失败"})

        if invite_code:
            # 处理第三方渠道的用户信息
            CoopRegister(request).all_processors_for_user_register(user, invite_code)
            # set_promo_user(request, user, invitecode=invite_code)
            # save_to_binding(user, request)

        if device['device_type'] == "pc":
            auth_user = authenticate(identifier=identifier, password=password)
            auth_login(request, auth_user)

        if not AntiForAllClient(request).anti_delay_callback_time(user.id, device, channel):
            tools.register_ok.apply_async(kwargs={"user_id": user.id, "device": device})

        #add by Yihen@20151020, 用户填写手机号不写密码即可完成注册, 给用户发短信,不要放到register_ok中去，保持原功能向前兼容
        if request.DATA.get('IGNORE_PWD'):
            send_messages.apply_async(kwargs={
                "phones": [identifier,],
                "messages": [u'您已成功注册网利宝,用户名为'+identifier+u';默认登录密码为'+password+u',赶紧登录领取福利！【网利科技】',]
            })

            logger.debug("此次 channel:%s" %(channel))
            if channel == 'maimai1':
                activity = Activity.objects.filter(code='maimai1').first()
                logger.debug("脉脉渠道的使用Activity是：%s" % (activity,))
                try:
                    redpack = WanglibaoUserGift.objects.create(
                        identity=identifier,
                        activity=activity,
                        rules=WanglibaoActivityGift.objects.first(),#随机初始化一个值
                        type=1,
                        valid=1
                    )
                except Exception, reason:
                    logger.debug("创建用户的领奖记录抛异常，reason：%s" % (reason,))

            if channel == 'h5chuanbo':
                key = 'share_redpack'
                shareconfig = Misc.objects.filter(key=key).first()
                if shareconfig:
                    shareconfig = json.loads(shareconfig.value)
                    if type(shareconfig) == dict:
                        is_attention = shareconfig.get('is_attention', '')
                        attention_code = shareconfig.get('attention_code', '')

                if is_attention:
                    activity = Activity.objects.filter(code=attention_code).first()
                    redpack = WanglibaoUserGift.objects.create(
                        identity=identifier,
                        activity=activity,
                        rules=WanglibaoActivityGift.objects.first(),#随机初始化一个值
                        type=1,
                        valid=0
                    )
                    dt = timezone.datetime.now()
                    redpack_event = RedPackEvent.objects.filter(invalid=False, id=755, give_start_at__lte=dt, give_end_at__gte=dt).first()
                    if redpack_event:
                        logger.debug("给用户：%s 发送红包:%s " %(user, redpack_event,))
                        redpack_backends.give_activity_redpack(user, redpack_event, 'pc')
                        redpack.valid = 1
                        redpack.save()
        try:
            openid = request.session.get('openid')
            if openid:
                w_user = WeixinUser.objects.get(openid=openid)
                bindUser(w_user, request.user)
        except Exception, e:
            logger.debug("fwh register bind error, error_message:::%s"%e.message)
        if channel in ('weixin_attention', 'maimai1'):
            return Response({"ret_code": 0, 'amount': 120, "message": u"注册成功"})
        else:
            return Response({"ret_code": 0, "message": u"注册成功"})


class WeixinRegisterAPIView(APIView):
    """
        wechat register
    """
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        """ 
            modified by: Yihen@20150812
            descrpition: if(line333~line334)的修改，针对特定的渠道延迟返积分、发红包等行为，防止被刷单
        """
        identifier = request.DATA.get('identifier', "").strip()
        validate_code = request.DATA.get('validate_code', "").strip()
        channel = request.session.get(settings.PROMO_TOKEN_QUERY_STRING, None)

        if not identifier or not validate_code:
            return Response({"ret_code": 30021, "message": "信息输入不完整"})

        identifier_type = detect_identifier_type(identifier)
        if identifier_type != 'phone':
            return Response({"ret_code": 30022, "message": u"请输入正确的手机号"})

        status, message = validate_validation_code(identifier, validate_code)
        if status != 200:
            # Modify by hb on 2015-12-02
            #return Response({"ret_code": 30023, "message": "验证码输入错误"})
            return Response({"ret_code": 30023, "message": message})

        #if User.objects.filter(wanglibaouserprofile__phone=identifier,
        #                       wanglibaouserprofile__phone_verified=True).exists():
        if User.objects.filter(wanglibaouserprofile__phone=identifier).first():
            return Response({"ret_code": 30024, "message": "该手机号已经注册"})

        invite_code = request.DATA.get('invite_code', "").strip()
        if invite_code:
            try:
                PromotionToken.objects.get(token=invite_code)
            except:
                return Response({"ret_code": 30025, "message": "邀请码错误"})

        password = generate_validate_code()
        user = create_user(identifier, password, "")
        if not user:
            return Response({"ret_code": 30025, "message": u"注册失败"})

        if invite_code:
            set_promo_user(request, user, invitecode=invite_code)
        auth_user = authenticate(identifier=identifier, password=password)
        auth_login(request, auth_user)
        send_rand_pass(identifier, password)

        device = split_ua(request)
        if not AntiForAllClient(request).anti_delay_callback_time(user.id, device, channel):
            tools.register_ok.apply_async(kwargs={"user_id": user.id, "device": device})

        return Response({"ret_code": 0, "message": "注册成功"})


# 客户端升级
class ClientUpdateAPIView(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        device_type = request.DATA.get("device_type", "")
        if not device_type or device_type not in ("iPhone", "iPad", "android"):
            return Response({"ret_code": 30101, "message": "信息输入有误"})

        key = device_type.lower() + "_update"
        sets = Misc.objects.filter(key=key).first()
        if not sets:
            return Response({"ret_code": 30102, "message": "This is no update"})
        try:
            info = json.loads(sets.value)
            return Response({"ret_code": 0, "message": "ok", "data": info})
        except Exception, e:
            return Response({"ret_code": 30103, "message": "This is no update"})


class PushTestView(APIView):
    permission_classes = ()

    def get(self, request):
        push_user_id = request.GET.get("push_user_id", "921913645184221981")
        push_channel_id = request.GET.get("push_channel_id", "4922700431463139292")


        #push_user_id = request.GET.get("push_user_id", "1033966060923467900")
        #push_channel_id = request.GET.get("push_channel_id", "4138455529717951568")

        push_user_id = request.GET.get("push_user_id", "781430269530794382")
        push_channel_id = request.GET.get("push_channel_id", "5422135652350005874")
        from wanglibao_sms import bae_channel

        channel = bae_channel.BaeChannel()
        message = {"message": "push Test<br/><br/><a href='http://www.wanglibao.com'>网利宝</a><br/>", "user_id":8731, "type":"in"}
        msg_key = "wanglibao_staging"
        res, cont = channel.pushIosMessage(push_user_id, push_channel_id, message, msg_key)
        #res, cont = channel.pushAndroidMessage(push_user_id, push_channel_id, message, msg_key)
        return Response({"ret_code": 0, "message": cont})


class IdValidateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        name = request.DATA.get("name", "").strip()
        id_number = request.DATA.get("id_number", "").strip()
        device = split_ua(request)

        if not name or not id_number:
            return Response({"ret_code": 30051, "message": u"信息输入不完整"})

        user = request.user
        profile = WanglibaoUserProfile.objects.filter(user=user).first()
        if profile.id_is_valid:
            return Response({"ret_code": 30055, "message": u"您已认证通过，请勿重复认证。如有问题，请联系客服 4008-588-066"})

        verify_counter, created = VerifyCounter.objects.get_or_create(user=user)

        if verify_counter.count >= 3:
            return Response({"ret_code": 30052, "message": u"验证次数超过三次，请联系客服进行人工验证 4008-588-066"})

        id_verify_count = WanglibaoUserProfile.objects.filter(id_number=id_number).count()
        if id_verify_count >= 1:
            return Response({"ret_code": 30053, "message": u"一个身份证只能绑定一个帐号, 请尝试其他身份证或联系客服 4008-588-066"})

        try:
            verify_record, error = verify_id(name, id_number)
        except:
            return Response({"ret_code": 30054, "message": u"验证失败，拨打客服电话进行人工验证"})

        verify_counter.count = F('count') + 1
        verify_counter.save()

        if error or not verify_record.is_valid:
            return Response({"ret_code": 30054, "message": u"验证失败，拨打客服电话进行人工验证"})

        user.wanglibaouserprofile.id_number = id_number
        user.wanglibaouserprofile.name = name
        user.wanglibaouserprofile.id_is_valid = True
        user.wanglibaouserprofile.id_valid_time = timezone.now()
        user.wanglibaouserprofile.save()

        device = split_ua(request)
        tools.idvalidate_ok.apply_async(kwargs={"user_id": user.id, "device": device})

        # 处理第三方用户实名回调
        CoopRegister(self.request).process_for_validate(user)

        return Response({"ret_code": 0, "message": u"验证成功"})


class SendVoiceCodeAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        phone_number = request.DATA.get("phone", "").strip()
        if not phone_number or not phone_number.isdigit():
            return Response({"ret_code": 30111, "message": u"信息输入不完整"})

        if not re.match("^((13[0-9])|(15[^4,\\D])|(14[5,7])|(17[0,5,9])|(18[^4,\\D]))\\d{8}$", phone_number):
            return Response({"ret_code": 30112, "message": u"手机号输入有误"})

        phone_validate_code_item = PhoneValidateCode.objects.filter(phone=phone_number).first()
        if phone_validate_code_item:
            count = phone_validate_code_item.code_send_count
            if count >= 6:
                return Response({"ret_code": 30113, "message": u"该手机号验证次数过于频繁，请联系客服人工注册"})

            phone_validate_code_item.code_send_count += 1
            phone_validate_code_item.save()
        else:
            now = timezone.now()
            phone_validate_code_item = PhoneValidateCode()
            validate_code = generate_validate_code()
            phone_validate_code_item.validate_code = validate_code
            phone_validate_code_item.phone = phone_number
            phone_validate_code_item.last_send_time = now
            phone_validate_code_item.code_send_count = 1
            phone_validate_code_item.is_validated = False
            phone_validate_code_item.save()

        status, cont = backends.YTXVoice.verify(phone_number, phone_validate_code_item.validate_code)
        logger.info("voice_code: %s" % cont)
        return Response({"ret_code": 0, "message": "ok"})


class SendVoiceCodeTwoAPIView(APIView):
    permission_classes = ()
    throttle_classes = (UserRateThrottle,)

    def post(self, request):
        phone_number = request.DATA.get("phone", "").strip()
        if not phone_number or not phone_number.isdigit():
            return Response({"ret_code": 30121, "message": u"信息输入不完整"})

        if not re.match("^((13[0-9])|(15[^4,\\D])|(14[5,7])|(17[0,5,9])|(18[^4,\\D]))\\d{8}$", phone_number):
            return Response({"ret_code": 30122, "message": u"手机号输入有误"})

        user = User.objects.filter(wanglibaouserprofile__phone=phone_number).first()
        if not user:
            return Response({"ret_code": 30123, "message": u"手机号不存在"})

        phone_validate_code_item = PhoneValidateCode.objects.filter(phone=phone_number).first()
        if phone_validate_code_item:
            phone_validate_code_item.code_send_count += 1
            phone_validate_code_item.save()
        else:
            now = timezone.now()
            phone_validate_code_item = PhoneValidateCode()
            validate_code = generate_validate_code()
            phone_validate_code_item.validate_code = validate_code
            phone_validate_code_item.phone = phone_number
            phone_validate_code_item.last_send_time = now
            phone_validate_code_item.code_send_count = 1
            phone_validate_code_item.is_validated = False
            phone_validate_code_item.save()

        status, cont = backends.YTXVoice.verify(phone_number, phone_validate_code_item.validate_code)
        logger.info("voice_code2: %s" % cont)
        return Response({"ret_code": 0, "message": "ok"})


# 云通讯语音验证码回调
class YTXVoiceCallbackAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        action = request.DATA.get("action", "").strip()
        call_sid = request.DATA.get("callSid", "").strip()
        phone = request.DATA.get("number", "").strip()
        state = request.DATA.get("state", "").strip()
        duration = request.DATA.get("duration", "").strip()

        if not action or not phone or not state:
            return Response({"statuscode": "1"})

        return Response({"statuscode": "000000"})


class LatestDataAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        now = datetime.now()
        today = datetime(now.year, now.month, now.day, 23, 59, 59)
        start = today - timedelta(30)
        ams = ProductAmortization.objects.filter(settlement_time__range=(start, today), settled=True)
        if not ams:
            return Response({"ret_code": 0, "message": "ok", "p2p_nums": 0, "amorization_amount": 0})
        else:
            amount = 0
            for x in ams:
                amount += x.principal + x.interest + x.penal_interest
            return Response({"ret_code": 0, "message": "ok", "p2p_nums": len(ams), "amorization_amount": amount})


class ShareUrlAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        rs = Misc.objects.filter(key="app_share_url").first()
        if not rs:
            return Response({"ret_code": 30141, "message": u"没有分享数据"})
        try:
            body = json.loads(rs.value)
        except:
            return Response({"ret_code": 30142, "message": u"没有分享数据"})
        if type(body) != dict:
            body = {}
        return Response({"ret_code": 0, "message": "ok", "data": body})

class DepositGateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        rs = Misc.objects.filter(key="pay_gate").first()
        try:
            obj = json.loads(rs.value)
        except:
            return Response({"ret_code":0, "gate":"kuai"})

        return Response({"ret_code":0, "data":obj})

       # if "gate" in obj:
       #     if obj['gate'] == "kuai":
       #         if "notice" in obj:
       #             return Response({"ret_code":0, "gate":"kuai", "notice":obj['notice']})
       #         else:
       #             return Response({"ret_code":0, "gate":"kuai", "notice":""})
       #     else:
       #         if "notice" in obj:
       #             return Response({"ret_code":0, "gate":"yee", "notice":obj['notice']})
       #         else:
       #             return Response({"ret_code":0, "gate":"yee", "notice":""})
       # else:
       #     return Response({"ret_code":0, "gate":"kuai"})

class TopsOfDayView(APIView):
    """
    得到某一天的排行榜
    """
    permission_classes = ()

    def post(self, request):

        try:
            day = request.DATA.get('day', "")
            top = Top()
            records = top.certain_day(int(day))
            isvalid = 1
            if len(records) == 0 and (datetime.utcnow().date() - top.activity_start.date()).days > int(day):
                isvalid = 0
                pass
        except Exception, e:
            return Response({"ret_code": -1, "records": list()})

        return Response({"ret_code": 0, "records": records, "isvalid": isvalid})


class TopsOfWeekView(APIView):
    """
    得到某一周的排行榜
    """
    permission_classes = ()

    def post(self, request):
        try:
            week = request.DATA.get('day', "")
            top = Top()
            records = top.certain_week(int(week))
            isvalid = 1
            if len(records) == 0 and (datetime.utcnow().date() - top.activity_start.date()).days > int(week):
                isvalid = 0
        except Exception, e:
            return Response({"ret_code": -1, "records": list()})

        return Response({"ret_code": 0, "records": records, "isvalid": isvalid})

import random
import operator

class TopsOfEaringView(APIView):
    """
        得到全民淘金前十
    """
    permission_classes = ()
    def post(self, request):
        try:

            init_datas = [("133*****423",143203),("139*****254",138902),("138*****098",121001.4),
                          ("133*****409",109923),("137*****534",99407),("137*****341",84203.6),
                          ("186*****908",78002),("130*****691",73032),("139*****582",50367)]
            records = []
            key = 'virtual_incomes'
            rs = Misc.objects.filter(key=key).first()
            if rs:
                virtual_incomes = json.loads(rs.value)
                for virtual_income in virtual_incomes['virtual_incomes']:
                    records.append({'phone':virtual_income[0], 'amount':Decimal(virtual_income[1]).quantize(Decimal('0.0'))})

            else:
                misc = Misc()
                misc.key = 'virtual_incomes'
                misc.value = json.dumps({key:init_datas})
                misc.description = "全民淘金排行虚拟数据"
                misc.save()
                for data in init_datas:
                    records.append({'phone':data[0], 'amount':Decimal(data[1]).quantize(Decimal('0.0'))})

            incomes = Income.objects.select_related('user').select_related('user__wanglibaouserprofile').values('user__wanglibaouserprofile__phone').annotate(sum_amount=Sum('earning')).order_by('-sum_amount')[0]

            records.append({'phone':safe_phone_str1(incomes['user__wanglibaouserprofile__phone']), 'amount':incomes['sum_amount']})
            records.sort(key=operator.itemgetter('amount'), reverse=True)
        except Exception, e:
            return Response({"ret_code": -1, "records": list()})
        return Response({"ret_code": 0, "records": records})

class TopsOfMonthView(APIView):
    """
    得到某一月的排行榜
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response({"ret_code": 0, "message":"ok"})

class UserExisting(APIView):
    permission_classes = ()

    def get(self, request, identifier, format=None):
        """
        Get whether the user existing
        """

        #query = Q(email=identifier) \
        #        | \
        #        (Q(wanglibaouserprofile__phone=identifier) &
        #         Q(wanglibaouserprofile__phone_verified=True))
        user = User.objects.filter(wanglibaouserprofile__phone=identifier).first()
        if user:
            return Response({"existing":True})
        else:
            return Response({"existing":False})

        #try:
        #    User.objects.get(query)
        #
        #    return Response({
        #                        "existing": True
        #                    }, status=200)
        #except User.DoesNotExist:
        #    return Response({
        #                        "existing": False
        #                    }, status=400)


class UserHasLoginAPI(APIView):
    """
        判断用户是否已经登录
    """
    permission_classes = ()

    def post(self, request):
        if not request.user.is_authenticated():
            return Response({"login": False})
        else:
            return Response({"login": True})

class IdValidate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        form = IdVerificationForm(request, request.POST)
        # 黑客程序就成功
        user = self.request.user
        now = timezone.now()

        # interval = (now - user.date_joined).seconds
        # if interval < 40:
        #     return Response({
        #                         "message": u"认证成功"
        #                     }, status=200)

        if form.is_valid():

            # name = request.DATA.get("name", "")
            # id_number = request.DATA.get("id_number", "")

            if request.DATA.get("captcha_1"):
                return Response({
                                    "message": u"实名认证成功..",
                                    "error_number": ErrorNumber.id_verify_times_error
                                }, status=200)

            name = form.cleaned_data['name']
            id_number = form.cleaned_data['id_number']

            verify_counter, created = VerifyCounter.objects.get_or_create(user=user)

            if verify_counter.count >= 3:
                return Response({
                                    "message": u"验证次数超过三次，请联系客服进行人工验证 4008-588-066",
                                    "error_number": ErrorNumber.try_too_many_times
                                }, status=400)

            id_verify_count = WanglibaoUserProfile.objects.filter(id_number=id_number).count()
            if id_verify_count >= 1:
                return Response({
                                    "message": u"一个身份证只能绑定一个帐号, 请尝试其他身份证或联系客服 4008-588-066",
                                    "error_number": ErrorNumber.id_verify_times_error
                                }, status=400)

            verify_record, error = verify_id(name, id_number)

            verify_counter.count = F('count') + 1
            verify_counter.save()

            if error or not verify_record.is_valid:
                return Response({
                                    "message": u"验证失败，拨打客服电话进行人工验证",
                                    "error_number": ErrorNumber.unknown_error
                                }, status=400)

            user.wanglibaouserprofile.id_number = id_number
            user.wanglibaouserprofile.name = name
            user.wanglibaouserprofile.id_is_valid = True
            user.wanglibaouserprofile.id_valid_time = timezone.now()
            user.wanglibaouserprofile.save()

            device = split_ua(request)
            tools.idvalidate_ok.apply_async(kwargs={"user_id": user.id, "device": device})

            # 处理第三方用户实名回调
            CoopRegister(self.request).process_for_validate(user)

            return Response({ "validate": True }, status=200)

        else:
            return Response({
                                "message": u"验证码错误",
                                "error_number": ErrorNumber.unknown_error
                            }, status=400)


class AdminIdValidate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        phone = request.DATA.get("phone", "")
        name = request.DATA.get("name", "")
        id_number = request.DATA.get("id_number", "")

        verify_record, error = verify_id(name, id_number)

        if error:
            return Response({
                                "message": u"验证失败",
                                "error_number": ErrorNumber.unknown_error
                            }, status=400)

        #user = get_user_model().objects.get(wanglibaouserprofile__phone=phone)
        user = User.objects.get(wanglibaouserprofile__phone=phone)
        user.wanglibaouserprofile.id_number = id_number
        user.wanglibaouserprofile.name = name
        user.wanglibaouserprofile.id_is_valid = True
        user.wanglibaouserprofile.id_valid_time = timezone.now()
        user.wanglibaouserprofile.save()

        return Response({
                            "validate": True
                        }, status=200)

class LoginAPIView(DecryptParmsAPIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        identifier = self.params.get("identifier", "")
        password = self.params.get("password", "")

        if not identifier or not password:
            return Response({"token":"false", "message":u"用户名或密码错误"}, status=400)

        user = authenticate(identifier=identifier, password=password)

        if not user:
            return Response({"token":"false", "message":u"用户名或密码错误"}, status=400)
        if not user.is_active:
            return Response({"token":"false", "message":u"用户已被关闭"}, status=400)
        if user.wanglibaouserprofile.frozen:
            return Response({"token":"false", "message":u"用户已被冻结"}, status=400)

        push_user_id = request.DATA.get("user_id", "")
        push_channel_id = request.DATA.get("channel_id", "")
        # 设备类型，默认为IOS
        device_type = request.DATA.get("device_type", "ios")
        if device_type not in ("ios", "android"):
            return Response({'message': "device_type error"}, status=status.HTTP_200_OK)

        if push_user_id and push_channel_id:
            pu = UserPushId.objects.filter(push_user_id=push_user_id).first()
            exist = False
            if not pu:
                pu = UserPushId()
                pu.device_type = device_type
                exist = True
            if exist or pu.user != user or pu.push_channel_id != push_channel_id:
                pu.user = user
                pu.push_user_id = push_user_id
                pu.push_channel_id = push_channel_id
                pu.save()
        token, created = Token.objects.get_or_create(user=user)
        # if not created:
        #     token.delete()
        #     token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, "user_id":user.id}, status=status.HTTP_200_OK)

class ObtainAuthTokenCustomized(ObtainAuthToken):
    permission_classes = ()
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid():
            push_user_id = request.DATA.get("user_id", "")
            push_channel_id = request.DATA.get("channel_id", "")
            # 设备类型，默认为IOS
            device_type = request.DATA.get("device_type", "ios")
            if device_type not in ("ios", "android"):
                return Response({'message': "device_type error"}, status=status.HTTP_200_OK)

            if push_user_id and push_channel_id:
                pu = UserPushId.objects.filter(push_user_id=push_user_id).first()
                exist = False
                if not pu:
                    pu = UserPushId()
                    pu.device_type = device_type
                    exist = True
                if exist or pu.user != serializer.object['user'] or pu.push_channel_id != push_channel_id:
                    pu.user = serializer.object['user']
                    pu.push_user_id = push_user_id
                    pu.push_channel_id = push_channel_id
                    pu.save()
            token, created = Token.objects.get_or_create(user=serializer.object['user'])
            return Response({'token': token.key, "user_id":serializer.object['user'].id}, status=status.HTTP_200_OK)
        else:
            device_type = request.DATA.get("device_type", "ios")
            if device_type == "ios":
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'token': "false"}, status=status.HTTP_200_OK)

def get_public_statistics():
    today = datetime.now()
    today_start = local_to_utc(datetime(today.year, today.month, today.day), 'min')

    today_user = User.objects.filter(date_joined__gte=today_start).aggregate(Count('id'))
    today_amount = P2PRecord.objects.filter(create_time__gte=today_start, catalog='申购').aggregate(Sum('amount'))
    today_num = P2PRecord.objects.filter(create_time__gte=today_start, catalog='申购').values('id').count()

    all_user = User.objects.all().aggregate(Count('id'))
    all_amount = P2PRecord.objects.filter(catalog='申购').aggregate(Sum('amount'))
    all_num = P2PRecord.objects.filter(catalog='申购').values('id').count()

    data = {
        'today_num': today_num,
        'today_user': today_user['id__count'],
        'today_amount': today_amount['amount__sum'],

        'all_num': all_num,
        'all_user': all_user['id__count'],
        'all_amount': all_amount['amount__sum'],
    }

    return data


class Statistics(APIView):
    """
        数据统计,今日注册,投资等,总计注册,投资等
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = get_public_statistics()

        return Response(data, status=status.HTTP_200_OK)


class StatisticsInside(APIView):
    """
        昨日还款额 = 昨日还款本金 + 昨日还款利息
        昨日资金净流入 = 昨日投资额 - 昨日还款本金
        昨日新用户投资金额 = 昨日首次投资用户的全天投资总额
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        today_start = local_to_utc(datetime(today.year, today.month, today.day), 'min')
        yesterday_start = local_to_utc(datetime(yesterday.year, yesterday.month, yesterday.day), 'min')
        start_fmt = yesterday_start.strftime('%Y-%m-%d %H:%M:%S')
        end_fmt = today_start.strftime('%Y-%m-%d %H:%M:%S')

        # 昨日申购总额
        yesterday_amount = P2PRecord.objects.filter(create_time__gte=yesterday_start, create_time__lt=today_start)\
            .filter(catalog='申购').aggregate(Sum('amount'))

        # 昨日还款
        today_repayment = ProductAmortization.objects.filter(settled=True)\
            .filter(settlement_time__gte=today_start).aggregate(Sum('principal'), Sum('interest'))

        # 今日还款
        yesterday_repayment = ProductAmortization.objects.filter(settled=True)\
            .filter(settlement_time__gte=yesterday_start, settlement_time__lt=today_start)\
            .aggregate(Sum('principal'), Sum('interest'))

        amount_sum_yesterday = yesterday_amount['amount__sum'] if yesterday_amount['amount__sum'] else Decimal('0')
        principal_sum = yesterday_repayment['principal__sum'] if yesterday_repayment['principal__sum'] else Decimal('0')
        interest_sum = yesterday_repayment['interest__sum'] if yesterday_repayment['interest__sum'] else Decimal('0')

        # 昨日资金净流入
        yesterday_inflow = amount_sum_yesterday - principal_sum - interest_sum

        # 今日还款额
        today_repayment_total = (today_repayment['principal__sum'] if today_repayment['principal__sum'] else 0) + \
                                (today_repayment['interest__sum'] if today_repayment['interest__sum'] else 0)
        # 昨日还款额
        yesterday_repayment_total = (yesterday_repayment['principal__sum'] if yesterday_repayment['principal__sum'] else 0) \
                + (yesterday_repayment['interest__sum'] if yesterday_repayment['interest__sum'] else 0)

        # 昨日首投用户
        from django.db import connection
        cursor = connection.cursor()
        sql = "SELECT SUM(a.amount) as amount_sum FROM wanglibao_p2p_p2precord a, " \
              "(SELECT user_id, create_time FROM wanglibao_p2p_p2precord WHERE catalog='申购' GROUP BY user_id) b " \
              "WHERE a.user_id = b.user_id " \
              "AND b.create_time >= '{}' AND b.create_time < '{}' " \
              "AND a.create_time >= '{}' AND a.create_time < '{}' " \
              "AND a.catalog='申购';".format(start_fmt, end_fmt, start_fmt, end_fmt)
        cursor.execute(sql)
        fetchone = cursor.fetchone()

        yesterday_new_amount = fetchone[0] if fetchone[0] else 0

        # 公共数据

        data = {
            'today_repayment_total': today_repayment_total,  # 今日还款额
            'yesterday_inflow': yesterday_inflow,  # 昨日资金净流入
            'yesterday_repayment_total': yesterday_repayment_total,  # 昨日还款额
            'yesterday_new_amount': yesterday_new_amount  # 昨日新用户投资金额
        }

        data.update(get_public_statistics())

        return Response(data, status=status.HTTP_200_OK)


class InvestRecord(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        p2p = request.DATA.get("p2p", "")
        page = request.DATA.get("page", "")
        if p2p == "" or page == "":
            return []

        product = P2PProduct.objects.filter(pk=p2p).first()
        records = P2PRecord.objects.filter(product=product, catalog=u'申购').select_related('user__wanglibaouserprofile')

        limit = 30
        paginator = Paginator(records, limit)

        try:
            p2p_records = paginator.page(page)
        except PageNotAnInteger:
            p2p_records = paginator.page(1)
        except Exception:
            p2p_records = paginator.page(paginator.num_pages)

        result = [{'create_time': timezone.localtime(trade_record.create_time).strftime("%Y-%m-%d"),
                   'user': safe_phone_str(trade_record.user.wanglibaouserprofile.phone),
                   'amount': trade_record.amount
                  } for trade_record in p2p_records]
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

obtain_auth_token = ObtainAuthTokenCustomized.as_view()


class MobileDownloadAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        channel = self.request.GET.get('channel', '')
        if channel and channel == 'weipai':
            if "HTTP_USER_AGENT" not in request.META:
                return HttpResponseRedirect('https://www.wanglibao.com/static/wanglibao_weipai.apk')

            useragent = request.META['HTTP_USER_AGENT'].lower()

            if "iphone" in useragent or "ipad" in useragent:
                return HttpResponseRedirect('https://itunes.apple.com/cn/app/wang-li-bao/id881326898?mt=8')
            else:
                return HttpResponseRedirect('https://www.wanglibao.com/static/wanglibao_weipai.apk')
        else:

            if "HTTP_USER_AGENT" not in request.META:
                return HttpResponseRedirect('http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao')

            useragent = request.META['HTTP_USER_AGENT'].lower()

            if "iphone" in useragent or "ipad" in useragent:
                return HttpResponseRedirect('https://itunes.apple.com/cn/app/wang-li-bao/id881326898?mt=8')
            else:
                return HttpResponseRedirect('http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao')


class KuaipanPurchaseListAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        trade_records = P2PRecord.objects.filter(catalog=u'申购').select_related('user').select_related(
            'user__wanglibaouserprofile')[:100]

        result = [{'purchase_time': timezone.localtime(trade_record.create_time).strftime("%Y-%m-%d %H:%M:%S"),
                   'userid': safe_phone_str(trade_record.user.wanglibaouserprofile.phone),
                   'amount': trade_record.amount
                  } for trade_record in trade_records]

        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


class GestureAddView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        add user gesture_pwd
        """
        try:
            gesture_pwd = request.DATA.get("gesture_pwd", "").strip()
        except:
            return Response({"ret_code": 30209, "message": u"参数类型错误"})

        if not gesture_pwd:
            return Response({"ret_code": 30201, "message": u"参数错误"})

        try:
            int(gesture_pwd)
        except:
            return Response({"ret_code": 30207, "message": u"手势密码类型错误"})

        if not gesture_pwd.isdigit() or ('0' in gesture_pwd):
            return Response({"ret_code": 30208, "message": u"手势密码不合法"})

        if not 4 <= len(gesture_pwd) <= 9:
            return Response({"ret_code": 30202, "message": u"手势密码长度需要在4-9位之间"})

        if len(gesture_pwd) > len(set(gesture_pwd)):
            return Response({"ret_code": 30203, "message": u"手势密码不能有重复的点"})

        phone = request.user.wanglibaouserprofile.phone
        u_profile = WanglibaoUserProfile.objects.filter(user=request.user, phone=phone)
        if not u_profile.exists():
            return Response({"ret_code": 30204, "message": u"用户不存在"})
        else:
            u_profile_object = u_profile.first()
            if u_profile_object.gesture_pwd:
                return Response({"ret_code": 30205, "message": u"手势密码已存在"})
            if u_profile_object.gesture_is_enabled:
                return Response({"ret_code": 30206, "message": u"手势密码已开启，无法重复添加"})
            u_profile_object.gesture_pwd = gesture_pwd
            u_profile_object.gesture_is_enabled = True
            u_profile_object.save()

        return Response({"ret_code": 0, "message": u"设置成功"})


class GestureUpdateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        update user gesture_pwd
        """
        try:
            gesture_pwd = request.DATA.get("gesture_pwd", "").strip()
        except:
            return Response({"ret_code": 30218, "message": u"参数类型错误"})

        if not gesture_pwd:
            return Response({"ret_code": 30211, "message": u"参数错误"})

        try:
            int(gesture_pwd)
        except:
            return Response({"ret_code": 30215, "message": u"手势密码类型错误"})

        if not gesture_pwd.isdigit() or ('0' in gesture_pwd):
            return Response({"ret_code": 30216, "message": u"手势密码不合法"})

        if not 4 <= len(gesture_pwd) <= 9:
            return Response({"ret_code": 30212, "message": u"手势密码需要在4-9位之间"})

        if len(gesture_pwd) > len(set(gesture_pwd)):
            return Response({"ret_code": 30213, "message": u"手势密码不能有重复的点"})

        phone = request.user.wanglibaouserprofile.phone
        u_profile = WanglibaoUserProfile.objects.filter(user=request.user, phone=phone)
        if not u_profile.exists():
            return Response({"ret_code": 30214, "message": u"用户不存在"})

        if u_profile.filter(gesture_is_enabled=False).exists():
            return Response({"ret_code": 30217, "message": u"手势密码在停用状态，不能修改"})

        u_profile_object = u_profile.filter(gesture_is_enabled=True).first()
        u_profile_object.gesture_pwd = gesture_pwd
        u_profile_object.save()

        return Response({"ret_code": 0, "message": u"设置成功"})


class GestureIsEnabledView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        gesture_is_enabled = request.DATA.get("gesture_is_enabled", "")

        try:
            gesture_is_enabled = int(gesture_is_enabled)
        except:
            return Response({"ret_code": 30221, "message": u"参数不合法"})

        if gesture_is_enabled not in (0, 1):
            return Response({"ret_code": 30222, "message": u"参数错误"})

        phone = request.user.wanglibaouserprofile.phone
        u_profile = WanglibaoUserProfile.objects.filter(user=request.user, phone=phone)
        if not u_profile.exists():
            return Response({"ret_code": 30223, "message": u"用户不存在"})

        if u_profile.filter(gesture_is_enabled=gesture_is_enabled).exists():
            return Response({"ret_code": 30224, "message": u"手势密码状态未修改"})

        u_profile_object = u_profile.first()
        u_profile_object.gesture_is_enabled = gesture_is_enabled
        u_profile_object.save()

        return Response({"ret_code": 0, "message": u"设置成功"})


class GuestCheckView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user

        p2p_record = P2PRecord.objects.filter(user=user, catalog='申购').first()

        # 已经购买， 不是新用户
        if p2p_record:
            return Response({"ret_code": 1, "message": u"不是新用户，不符合活动标准！"})

        introduced_by = IntroducedBy.objects.filter(user=user, channel__code='xunlei8').first()

        # 渠道是xunlei8
        if introduced_by:
            activity_record = ActivityRecord.objects.filter(user=user, activity__code='xunlei8').first()
            data = dict()
            data['has_rewarded'] = True if activity_record else False
            return Response({"ret_code": 0, "data": data})
        # 渠道不符合标准
        else:
            return Response({"ret_code": 2, "message": u"抱歉，不符合活动标准！"})


import hashlib
from random import randint

from django.contrib.auth import authenticate

from wanglibao_account.utils import create_user
from wanglibao_oauth2.models import Client


def generate_random_password(length=6):
    length = int(length)

    if length <= 0:
        raise Exception(u'密码长度不能小于或等于0')

    return ''.join([str(randint(0, 9)) for i in range(length)])


class RegisterOpenApiView(APIView):
    permission_classes = ()

    def _generate_sign(self, client_id, identifier, key):
        return hashlib.md5(client_id+identifier+key).hexdigest()

    def _cleaned_sign(self, client_id, identifier, key, sign):
        response_data = {}
        _sign = self._generate_sign(client_id, identifier, key)

        if _sign != sign:
            response_data = {
                'code': '40008',
                'message': u'签名错误'
            }

        return response_data

    def _cleaned_identifier(self, identifier):
        """
        since identifier must be a phone number
        So checking the format here is important
        """

        response_data = {}
        users = None

        identifier_type = detect_identifier_type(identifier)

        if identifier_type == 'phone':
            users = User.objects.filter(wanglibaouserprofile__phone=identifier)
        else:
            response_data = {
                'code': '40002',
                'message': u'不是有效的手机号'
            }

        if users and len(users) != 0:
            response_data = {
                'code': '40003',
                'message': u'该手机号已被注册'
            }

        return response_data

    def _clean_validate_code(self, identifier, v_code):
        identifier_type = detect_identifier_type(identifier)
        response_data = {}

        if identifier_type == 'phone':
            phone = identifier
            _status, message = validate_validation_code(phone, v_code)

            if _status != 200:
                response_data = {
                    'code': '40000',
                    'message': u'验证码错误'
                }

        return response_data

    def cleaned_data(self, client_id, sign, identifier, v_code):
        if not client_id:
            response_data = {
                'code': '40005',
                'message': u'平台标识不能为空'
            }
        elif not sign:
            response_data = {
                'code': '40007',
                'message': u'签名不能为空'
            }
        elif not identifier:
            response_data = {
                'code': '40001',
                'message': u'用户名不能为空'
            }
        elif not v_code:
            response_data = {
                'code': '40009',
                'message': u'验证码不能为空'
            }
        else:
            response_data = self._cleaned_identifier(identifier)
            if not response_data:
                response_data = self._clean_validate_code(identifier, v_code)

                if not response_data:
                    try:
                        client = Client.objects.get(client_id=client_id)
                    except Client.DoesNotExist:
                        return {
                            'code': '40006',
                            'message': u'无效平台标识'
                        }

                    client_id = client.client_id
                    client_secret = client.client_secret
                    response_data = self._cleaned_sign(client_id, identifier, client_secret, sign)

        return response_data

    def post(self, request):
        data = request.POST
        client_id = data.get('client_id', '').strip()
        sign = data.get('signature', '').strip()
        identifier = data.get('identifier', '').strip()
        v_code = data.get('validate_code', '').strip()

        response_data = self.cleaned_data(client_id, sign, identifier, v_code)
        if not response_data:
            password = generate_random_password()
            user = create_user(identifier, password, '')

            if user:
                # 处理第三方渠道的用户信息
                # CoopRegister(request).all_processors_for_user_register(user, invite_code)

                # 防作弊处理
                # if not AntiForAllClient(request).anti_delay_callback_time(user.id, device, channel):
                #     tools.register_ok.apply_async(kwargs={"user_id": user.id, "device": device})

                response_data = {
                    'code': '10000',
                    'message': u'success',
                    'usn': identifier,
                    'user_id': user.id
                }

                # 向用户发送随机生成的注册密码的短信消息
                send_messages.apply_async(kwargs={
                    "phones": [identifier, ],
                    "messages": [password, ]
                })
            else:
                response_data = {
                    'code': '40010',
                    'message': u'用户创建失败'
                }

        return HttpResponse(renderers.JSONRenderer().render(response_data,
                                                            'application/json'))

class InnerSysHandler(object):
    def ip_valid(self, request):
        INNER_IP = ("182.92.179.24", "10.171.37.235")
        client_ip = get_client_ip(request)
        return True if client_ip in INNER_IP else False

    def judge_valid(self, request):
        if not self.ip_valid(request):
            return False, u'IP没有通过验证'

        return True, u'通过验证'


class InnerSysSendSMS(APIView, InnerSysHandler):
    permission_classes = ()

    def post(self, request):
        phone = request.DATA.get("phone", None)
        message = request.DATA.get("message", None)
        logger.debug("phone:%s, message:%s" % (phone, message))
        if phone is None or message is None:
            return Response({"code": 1000, "message": u'传入的phone或message不全'})

        status, invalid_msg = super(InnerSysSendSMS, self).judge_valid(request)
        if not status:
            return Response({"code": 1001, "message": invalid_msg})

        send_messages.apply_async(kwargs={
                "phones": [phone, ],
                "messages": [message, ]
            })

        return Response({"code": 0, "message": u"短信发送成功"})


class InnerSysValidateID(APIView, InnerSysHandler):
    permission_classes = ()

    def param_is_valid(self, name, id):
        id_pattern = '\d{17}[0-9Xx]'
        return True if id and len(id) == 18 and re.match(id_pattern, id).group() else False

    def post(self, request):
        """
            要考虑已经做过验证的用户
        """
        name = request.DATA.get("name", None)
        id = request.DATA.get("id", None)

        if name is None or id is None:
            return Response({"code": 1000, "message": u'请发送完整的姓名及身份证号'})

        if not self.param_is_valid(name, id):
            return Response({"code": 1001, "message": u'传递的参数不合法'})

        status, message = self.judge_valid(request)
        if not status:  # 此步目前跳过
            return Response({"code": 1002, "message": message})

        profile = WanglibaoUserProfile.objects.filter(name=name, id_number=id, id_is_valid=True)
        if profile.exists():
            return Response({"code": 0, "message": u'用户以前已经验证过且验证通过'})

        try:
            logger.debug('name:%s, id:%s' % (name, id))
            verify_record, error = verify_id(name, id)
            logger.debug('name:%s, id:%s, verifiy_record:%s, error:%s' % (name, id, verify_record, error))
        except:
            return Response({"code": 1003, "message": u"验证失败，拨打客服电话进行人工验证"})
        else:
            if error or not verify_record.is_valid:
                return Response({"code": 1003, "message": u"验证失败，拨打客服电话进行人工验证"})
            else:
                return Response({"code": 0, "message": u"验证通过"})


class InnerSysSaveChannel(APIView, InnerSysHandler):
    permission_classes = ()

    def post(self, request):
        code = request.DATA.get("code", None)
        description = request.DATA.get("description", None)
        name = request.DATA.get("name", None)
        if not code or not description:
            return Response({"code": 1000, "message": u'渠道号或渠道描述为空值'})

        status, message = super(InnerSysSaveChannel, self).judge_valid(request)
        if not status:
            return Response({"code": 1001, "message": message})

        channel = Channels.objects.filter(code=code)
        if channel.exists():
            return Response({"code": 1002, "message": u'渠道号已经存在'})
        try:
            Channels.objects.create(name=name, code=code, description=description)
        except Exception, reason:
            return Response({"code": 1003, "message": u'创建渠道报异常,reason:{0}'.format(reason)})
        else:
            return Response({"code": 0, "message": u'创建渠道成功'})


class DistributeRedpackView(APIView):
    permission_classes = ()
    def post(self, request, phone):
        user = WanglibaoUserProfile.objects.filter(phone=phone).first()
        channel = request.session.get(settings.PROMO_TOKEN_QUERY_STRING, None)

        if channel == 'maimai1':
            phone_number = phone.strip()
            redpack = WanglibaoUserGift.objects.filter(identity=phone, activity__code='maimai1').first()
            if redpack:
                data = {
                    'ret_code': 0,
                    'message': u'用户已经领取了加息券',
                    'amount': redpack.amount,
                    'phone': phone_number
                }
                return HttpResponse(json.dumps(data), content_type='application/json')

            else:
                activity = Activity.objects.filter(code='maimai1').first()
                redpack = WanglibaoUserGift.objects.create(
                    identity=phone_number,
                    activity=activity,
                    rules=WanglibaoActivityGift.objects.first(),#随机初始化一个值
                    type=1,
                    valid=0
                )
                logger.debug("usergift表中为用户生成了获奖记录：%s" % (redpack,))
                user = WanglibaoUserProfile.objects.filter(phone=phone_number).first().user
                if user:
                    logger.debug("用户已经存在，开始给该用户发送加息券")
                    try:
                        redpack_id = ActivityRule.objects.filter(activity=activity).first().redpack
                    except Exception, reason:
                        logger.debug("从ActivityRule中获得redpack_id抛异常, reason:%s" % (reason, ))

                    try:
                        logger.debug("用户：%s 使用的加息券id:%s" %(phone_number, redpack_id))
                        redpack_event = RedPackEvent.objects.filter(id=780).first()
                    except Exception, reason:
                        logger.debug("从RedPackEvent中获得配置红包报错, reason:%s" % (reason, ))

                    try:
                        logger.debug("给用户 %s 发送加息券:%s" %(user, redpack_event))
                        msg = redpack_backends.give_activity_redpack(user, redpack_event, 'pc')
                        logger.debug("给用户 %s 发送加息券:%s, 返回状态值,:%s" %(user, redpack_event, msg))
                    except Exception, reason:
                        logger.debug("给用户发红包抛异常, reason:%s" % (reason, ))
                    else:
                        redpack.user = user
                        redpack.valid = 1
                        redpack.save()
                        data = {
                            'ret_code': 1000,
                            'message': u'下发加息券成功',
                            'amount': redpack.amount,
                            'phone': phone_number
                        }
                        return HttpResponse(json.dumps(data), content_type='application/json')


class DataCubeApiView(APIView):
    """
    数据魔方查询接口
    chenweibin@20151208
    """
    permission_classes = ()

    def __init__(self):
        super(DataCubeApiView, self).__init__()
        self.request_url = settings.DATACUBE_URL

    def get(self, request):
        try:
            data = requests.get(url=self.request_url).json()
            _response = {
                'ret_code': 10000,
                'message': 'success',
                'result': data,
            }
        except Exception, e:
            logger.exception('data cupe connect faild to %s' % self.request_url)
            logger.exception(e)
            _response = {
                'ret_code': 50001,
                'message': 'api error',
            }

        return HttpResponse(json.dumps(_response), content_type='application/json')


class BidHasBindingForChannel(APIView):
    """
    根据bid（第三方用户ID）判断该用户是否已经绑定指定渠道
    """

    permission_classes = ()

    def get(self, request, channel_code, bid):
        binding = Binding.objects.filter(btype=channel_code, bid=bid).first()
        if binding:
            response_data = {
                'ret_code': 10001,
                'message': u'该bid已经绑定'
            }
        else:
            response_data = {
                'ret_code': 10000,
                'message': u'该bid未绑定'
            }

        return HttpResponse(json.dumps(response_data), content_type='application/json')
