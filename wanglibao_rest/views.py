# encoding:utf-8

import json
import logging
import re
from datetime import timedelta, datetime, time
from django.db.models import Count, Sum

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.db.models import Q
from django.db.models import F
from rest_framework import generics, renderers
from django.http import HttpResponse
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from marketing.models import PromotionToken, Reward, RewardRecord
from marketing.utils import set_promo_user
from wanglibao_account.utils import create_user
from wanglibao_portfolio.models import UserPortfolio
from wanglibao_portfolio.serializers import UserPortfolioSerializer
from wanglibao_rest.serializers import AuthTokenSerializer
from wanglibao_sms.utils import send_validation_code, validate_validation_code, send_rand_pass, generate_validate_code
from wanglibao_sms.models import PhoneValidateCode
from wanglibao.const import ErrorNumber
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_account.models import VerifyCounter, UserPushId
from wanglibao_p2p.models import P2PRecord, ProductAmortization
from wanglibao_account.utils import verify_id, detect_identifier_type
from django.db import transaction
from wanglibao_sms import messages, backends
from django.utils import timezone
from wanglibao_account import message as inside_message
from misc.models import Misc
from wanglibao_account.forms import IdVerificationForm
from marketing.helper import RewardStrategy, which_channel, Channel
from wanglibao_rest.utils import search
from django.http import HttpResponseRedirect
from wanglibao.templatetags.formatters import safe_phone_str


logger = logging.getLogger(__name__)


class UserPortfolioView(generics.ListCreateAPIView):
    queryset = UserPortfolio.objects.all()
    serializer_class = UserPortfolioSerializer

    def get_queryset(self):
        user_pk = self.kwargs['user_pk']
        return self.queryset.filter(user_id=user_pk)


class SendValidationCodeView(APIView):
    """
    The phone validate view which accept a post request and send a validate code to the phone
    """
    permission_classes = ()
    throttle_classes = (UserRateThrottle,)

    def post(self, request, phone, format=None):
        phone_number = phone.strip()
        status, message = send_validation_code(phone_number)
        return Response({
                            'message': message
                        }, status=status)


class SendRegisterValidationCodeView(APIView):
    """
    The phone validate view which accept a post request and send a validate code to the phone
    """
    permission_classes = ()
    # throttle_classes = (UserRateThrottle,)

    def post(self, request, phone, format=None):
        phone_number = phone.strip()
        phone_check = WanglibaoUserProfile.objects.filter(phone=phone_number, phone_verified=True)
        if phone_check:
            return Response({
                                "message": u"该手机号已经被注册，不能重复注册",
                                "error_number": ErrorNumber.duplicate
                            }, status=400)

        phone_validate_code_item = PhoneValidateCode.objects.filter(phone=phone_number).first()
        if phone_validate_code_item:
            count = phone_validate_code_item.code_send_count
            if count > 6:
                return Response({
                                    "message": u"该手机号验证次数过于频繁，请联系客服人工注册",
                                    "error_number": ErrorNumber.duplicate
                                }, status=400)

        status, message = send_validation_code(phone_number)
        return Response({
                            'message': message
                        }, status=status)

    def dispatch(self, request, *args, **kwargs):
        return super(SendRegisterValidationCodeView, self).dispatch(request, *args, **kwargs)


class RegisterAPIView(APIView):
    permission_classes = ()
    # throttle_classes = (UserRateThrottle,)
    # serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        identifier = request.DATA.get('identifier', "")
        password = request.DATA.get('password', "")
        validate_code = request.DATA.get('validate_code', "")

        identifier = identifier.strip()
        password = password.strip()
        validate_code = validate_code.strip()

        if not identifier or not password or not validate_code:
            return Response({"ret_code": 30011, "message": "信息输入不完整"})

        if not 6 <= len(password) <= 20:
            return Response({"ret_code": 30012, "message": u"密码需要在6-20位之间"})

        identifier_type = detect_identifier_type(identifier)
        if identifier_type != 'phone':
            return Response({"ret_code": 30013, "message": u"手机号输入错误"})

        status, message = validate_validation_code(identifier, validate_code)
        if status != 200:
            return Response({"ret_code": 30014, "message": u"验证码输入错误"})

        if User.objects.filter(wanglibaouserprofile__phone=identifier,
                               wanglibaouserprofile__phone_verified=True).exists():
            return Response({"ret_code": 30015, "message": u"该手机号已经注册"})

        invite_code = request.DATA.get('invite_code', "")
        if invite_code:
            try:
                PromotionToken.objects.get(token=invite_code)
            except:
                return Response({"ret_code": 30016, "message": "邀请码错误"})

        # user = create_user(serializer.object['identifier'], serializer.object['password'], "")
        user = create_user(identifier, password, "")
        if invite_code:
            set_promo_user(request, user, invitecode=invite_code)

        title, content = messages.msg_register()
        inside_message.send_one.apply_async(kwargs={
            "user_id": user.id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })
        # todo save client info
        return Response({"ret_code": 0, "message": "注册成功"})



class WeixinRegisterAPIView(APIView):

    """
        wechat register
    """
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        identifier = request.DATA.get('identifier', "").strip()
        validate_code = request.DATA.get('validate_code', "").strip()

        if not identifier or not validate_code:
            return Response({"ret_code": 30021, "message": "信息输入不完整"})

        identifier_type = detect_identifier_type(identifier)
        if identifier_type != 'phone':
            return Response({"ret_code": 30022, "message": u"请输入正确的手机号"})

        status, message = validate_validation_code(identifier, validate_code)
        if status != 200:
            return Response({"ret_code": 30023, "message": "验证码输入错误"})

        if User.objects.filter(wanglibaouserprofile__phone=identifier,
                               wanglibaouserprofile__phone_verified=True).exists():
            return Response({"ret_code": 30024, "message": "该手机号已经注册"})

        invite_code = request.DATA.get('invite_code', "").strip()
        if invite_code:
            try:
                PromotionToken.objects.get(token=invite_code)
            except:
                return Response({"ret_code": 30025, "message": "邀请码错误"})

        password = generate_validate_code()
        # password = random.randint(100000, 999999)
        user = create_user(identifier, password, "")
        if invite_code:
            set_promo_user(request, user, invitecode=invite_code)
        auth_user = authenticate(identifier=identifier, password=password)
        auth_login(request, auth_user)
        send_rand_pass(identifier, password)

        title, content = messages.msg_register()
        inside_message.send_one.apply_async(kwargs={
            "user_id": auth_user.id,
            "title": title,
            "content": content,
            "mtype": "activityinfo"
        })
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
        from wanglibao_sms import bae_channel

        channel = bae_channel.BaeChannel()
        message = {"message": "push Test"}
        msg_key = "wanglibao_staging"
        res, cont = channel.pushIosMessage(push_user_id, push_channel_id, message, msg_key)
        return Response({"ret_code": 0, "message": cont})


class IdValidateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        name = request.DATA.get("name", "").strip()
        id_number = request.DATA.get("id_number", "").strip()

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
        user.wanglibaouserprofile.save()

        return Response({"ret_code": 0, "message": u"验证成功"})


class SendVoiceCodeAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        phone_number = request.DATA.get("phone", "").strip()
        if not phone_number or not phone_number.isdigit():
            return Response({"ret_code": 30111, "message": u"信息输入不完整"})

        if not re.match("^((13[0-9])|(15[^4,\\D])|(14[5,7])|(17[0,5,9])|(18[^4,\\D]))\\d{8}$", phone_number):
            return Response({"ret_code": 30112, "message": u"手机号输入有误"})

        #phone_check = WanglibaoUserProfile.objects.filter(phone=phone_number, phone_verified=True)
        #if phone_check:
        #    return Response({"ret_code":30112, "message": u"该手机号已经被注册，不能重复注册"})

        phone_validate_code_item = PhoneValidateCode.objects.filter(phone=phone_number).first()
        if phone_validate_code_item:
            count = phone_validate_code_item.code_send_count
            if count > 6:
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


#云通讯语音验证码回调
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
        start = today-timedelta(30)
        ams = ProductAmortization.objects.filter(settlement_time__range=(start, today), settled=True)
        if not ams:
            return Response({"ret_code": 0, "message": "ok", "p2p_nums":0, "amorization_amount":0})
        else:
            amount = 0
            for x in ams:
                amount += x.principal + x.interest + x.penal_interest
            return Response({"ret_code": 0, "message": "ok", "p2p_nums":len(ams), "amorization_amount":amount})

class ShareUrlAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        rs = Misc.objects.filter(key="app_share_url").first()
        if not rs:
            return Response({"ret_code": 30141, "message":u"没有分享数据"})
        try:
            body = json.loads(rs.value)
        except:
            return Response({"ret_code": 30142, "message":u"没有分享数据"})
        if type(body) != dict:
            body = {}
        return Response({"ret_code": 0, "message":"ok", "data":body})

class UserExisting(APIView):
    permission_classes = ()

    def get(self, request, identifier, format=None):
        """
        Get whether the user existing
        """

        query = Q(email=identifier) \
                | \
                (Q(wanglibaouserprofile__phone=identifier) &
                 Q(wanglibaouserprofile__phone_verified=True))

        try:
            get_user_model().objects.get(query)

            return Response({
                                "existing": True
                            }, status=200)
        except get_user_model().DoesNotExist:
            return Response({
                                "existing": False
                            }, status=400)


class IdValidate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        form = IdVerificationForm(request, request.POST)
        #黑客程序就成功
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
            user.wanglibaouserprofile.save()

            # 判断时间间隔太短的话就认定他是黑客，需要电话找客服索要激活码
            # if interval < 60:
            #     title,content = messages.msg_validate_fake()
            #     inside_message.send_one.apply_async(kwargs={
            #         "user_id":user.id,
            #         "title":title,
            #         "content":content,
            #         "mtype":"activity"
            #     })
            # else:

            # 实名认证 活动赠送
            channel = which_channel(user)
            rs = RewardStrategy(user)
            if channel == Channel.KUAIPAN:
                # 快盘来源
                rs.reward_user(u'50G快盘容量')

            return Response({
                                "validate": True
                            }, status=200)

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

        user = get_user_model().objects.get(wanglibaouserprofile__phone=phone)
        user.wanglibaouserprofile.id_number = id_number
        user.wanglibaouserprofile.name = name
        user.wanglibaouserprofile.id_is_valid = True
        user.wanglibaouserprofile.save()

        return Response({
                            "validate": True
                        }, status=200)


class ObtainAuthTokenCustomized(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid():
            push_user_id = request.DATA.get("user_id", "")
            push_channel_id = request.DATA.get("channel_id", "")
            #设备类型，默认为IOS
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
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Statistics(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())

        today_user = User.objects.filter(date_joined__range=(today_start, today_end)).aggregate(Count('id'))
        today_amount = P2PRecord.objects.filter(create_time__range=(today_start, today_end), catalog='申购').aggregate( Sum('amount'))

        today_num = P2PRecord.objects.filter(create_time__range=(today_start, today_end), catalog='申购')\
            .values('id').count()

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

        return Response(data, status=status.HTTP_200_OK)


obtain_auth_token = ObtainAuthTokenCustomized.as_view()


class MobileDownloadAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        useragent = request.META['HTTP_USER_AGENT']

        print useragent

        if search('iPhone', useragent):
            return HttpResponseRedirect('https://itunes.apple.com/cn/app/wang-li-bao/id881326898?mt=8')
        elif search('iPad', useragent):
            return HttpResponseRedirect('https://itunes.apple.com/cn/app/wang-li-bao/id881326898?mt=8')
        elif search('Android', useragent):
            return HttpResponseRedirect('http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao')
            # return HttpResponseRedirect('http://192.168.1.200:8000/static/wanglibao.apk')
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
