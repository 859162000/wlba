# /usr/bin/env python
# encoding: utf-8

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from wanglibao_profile.backends import trade_pwd_is_set, trade_pwd_set
from wanglibao_profile.serializers import ProfileSerializer
from wanglibao_account.models import VerifyCounter
from wanglibao.const import ErrorNumber
from wanglibao_account.utils import verify_id
from wanglibao_pay.models import Card
from wanglibao_account.utils import str_add_md5
from django.db.models import F
from wanglibao_redpack.backends import local_transform_str
from django.contrib.auth.models import User
from django.utils import timezone

class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Retrieve the current user's profile
        """
        user = request.user
        cards = Card.objects.filter(user=user)
        profile = user.wanglibaouserprofile

        idn = profile.id_number
        if len(idn) == 18:
            id_number = "%s********%s" % (idn[:6], idn[-4:])
        elif len(idn) == 15:
            id_number = "%s******%s" % (idn[:6], idn[-3:])
        else:
            id_number = "%s******%s" % (idn[:1], idn[-1:])

        dic = {
            "user":profile.user_id,
            "frozen":profile.frozen,
            "nick_name":profile.nick_name,
            "phone":profile.phone,
            "phone_verified":profile.phone_verified,
            "name":profile.name,
            "id_number":id_number,
            "id_is_valid":profile.id_is_valid,
            "id_valid_time":profile.id_valid_time if not profile.id_valid_time else local_transform_str(profile.id_valid_time),
            "shumi_request_token":profile.shumi_request_token,
            "shumi_request_token_secret":profile.shumi_request_token_secret,
            "shumi_access_token":profile.shumi_access_token,
            "shumi_access_token_secret":profile.shumi_access_token_secret,
            "risk_level":profile.risk_level,
            "investment_asset":profile.investment_asset,
            "investment_period":profile.investment_period,
            "deposit_default_bank_name":profile.deposit_default_bank_name,
            "is_invested": profile.is_invested,
            "cards_number":len(cards),
            "gesture_pwd": str_add_md5(str(profile.gesture_pwd)),
            "gesture_is_enabled": profile.gesture_is_enabled,
            "promo_token":user.promotiontoken.token,
            'trade_pwd_is_set': trade_pwd_is_set(profile.user_id)
        }
        return Response(dic)
        #serializer = ProfileSerializer(user.wanglibaouserprofile)
        #return Response(serializer.data)

    def put(self, request):
        """
        Update current user's profile
        """
        user = request.user
        name = request.DATA.get("name", "")
        id_number = request.DATA.get("id_number", "")

        profile_serializer = ProfileSerializer(user.wanglibaouserprofile, data=request.DATA, partial=True)
        if not profile_serializer.is_valid():
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        verify_counter, created = VerifyCounter.objects.get_or_create(user=user)

        if verify_counter.count >= 3:
            return Response({
                                "message": u"验证次数超过三次，请联系客服进行人工验证",
                                "error_number": ErrorNumber.try_too_many_times
                            }, status=400)

        verify_record, error = verify_id(name, id_number)

        verify_counter.count = F('count') + 1
        verify_counter.save()

        if error or not verify_record.is_valid:
            return Response({
                                "message": u"验证失败，拨打客服电话进行人工验证",
                                "error_number": ErrorNumber.unknown_error
                            }, status=400)

        profile_serializer.save()
        return Response(profile_serializer.data, status=status.HTTP_200_OK)

class TradePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        '''
        前段post的参数
        action_type: =1.设置初始密码；=2.使用旧交易密码修改新交易密码；=3.同时使用银行卡和身份证修改旧交易密码
        old_trade_pwd: 交易密码
        new_trade_pwd: 新交易密码
        card_id:   银行卡号
        citizen_id: 身份证号
	    requirement_check:requirement_check: =1只进行条件检查，校验旧密码或是银行卡，身份证时使用该参数， =0进行条件检查和设置交易密码
        :param request:
        :return:
        '''
        # def trade_pwd_set(user_id, action_type, new_trade_pwd=None, old_trade_pwd=None,  card_id=None, citizen_id=None):
        if request.DATA.get('requirement_check') == '1':
            requirement_check = True
        else:
            requirement_check = False

        result = trade_pwd_set(request.user.id,
                               request.DATA.get('action_type'),
                               new_trade_pwd= request.DATA.get('new_trade_pwd'),
                               old_trade_pwd=request.DATA.get('old_trade_pwd'),
                               card_id=request.DATA.get('card_id'),
                               citizen_id=request.DATA.get('citizen_id'),
                               only_requirement_check=requirement_check)
        return Response(result)
