# /usr/bin/env python
# encoding: utf-8

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from wanglibao_profile.serializers import ProfileSerializer
from wanglibao_account.models import VerifyCounter
from wanglibao.const import ErrorNumber
from wanglibao_account.utils import verify_id
from wanglibao_pay.models import Card
from wanglibao_account.utils import str_add_md5
from django.db.models import F


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Retrieve the current user's profile
        """
        user = request.user
        cards = Card.objects.filter(user=user)
        profile = user.wanglibaouserprofile

        dic = {
            "user":profile.user_id,
            "frozen":profile.frozen,
            "nick_name":profile.nick_name,
            "phone":profile.phone,
            "phone_verified":profile.phone_verified,
            "name":profile.name,
            "id_number":profile.id_number,
            "id_is_valid":profile.id_is_valid,
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
            "gesture_is_enabled": profile.gesture_is_enabled
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
