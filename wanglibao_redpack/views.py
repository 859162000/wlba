#!/usr/bin/env python
# encoding:utf-8


from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from wanglibao_redpack.backends import give_activity_redpack
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent
from wanglibao_redpack import backends
from wanglibao_rest import utils


class RedPacketView(TemplateView):
    #红包PC端页面
    template_name = ""

    def get_context_data(self, request, **kwargs):
        pass

    #PC兑换红包使用
    def post(self, request):
        pass

class RedPacketChangeAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    throttle_classes = (UserRateThrottle,)

    def post(self, request):
        token = request.DATA.get("token", "")
        device = utils.split_ua(request)
        user = request.user
        try:
            app_version = device['app_version']
        except KeyError:
            app_version = ''
        result = backends.exchange_redpack(token, device['device_type'], user, app_version)
        return Response(result)

class RedPacketListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        status = request.DATA.get("status", "")
        rtype = request.DATA.get("rtype", "")
        product_id = request.DATA.get("product_id", "")
        device = utils.split_ua(request)
        user = request.user
        try:
            app_version = device['app_version']
        except KeyError:
            app_version = ''
        result = backends.list_redpack(user, status, device['device_type'], product_id, rtype, app_version)
        return Response(result)

class RedPacketDeductAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        amount = request.DATA.get("amount", "").strip()
        redpack_amount = request.DATA.get("rpa", "").strip()
        result = backends.deduct_calc(amount, redpack_amount)
        return Response(result)


class RedPacketSelectAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        product_id = request.DATA.get("product_id", 0)
        if not product_id:
            return Response({"ret_code": 3001, "message": u"产品ID错误"})
        result = backends.get_interest_coupon(user, product_id)
        return Response(result)

class RequestPacketAPIView(APIView):
    """
    用户主动领取某个红包活动的红包
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        #必填
        user = request.user
        event = request.DATA.get("redpack_event_name")
        #选填
        device_type = request.DATA.get("device_type", "all")
        status, message = give_activity_redpack(user, event, device_type, just_one_packet=True)
        return Response(dict(status=status, message=message))
