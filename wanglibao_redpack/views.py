#!/usr/bin/env python
# encoding:utf-8


from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent
from wanglibao_redpack import backends


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

    def post(self, request):
        token = request.DATA.get("token", "")
        device_type = request.DATA.get("channelId", "")
        user = request.user
        result = backends.exchange_redpack(token, device_type, user)
        return Response(result)

class RedPacketListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        status = request.DATA.get("status", "")
        user = request.user
        result = backends.list_redpack(user, status)
        return Response(result)
