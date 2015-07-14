#!/usr/bin/env python
# encoding:utf-8

__author__ = 'zhanghe'


from wanglibao import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from wanglibao_banner.models import AppActivate
from wanglibao_rest.utils import split_ua


class AppActivateImageAPIView(APIView):
    """ app端查询启动活动图片 """

    permission_classes = ()

    SIZE_MAP = {'1': 'img_one', '2': 'img_two', '3': 'img_three'}
    DEVICE_MAP = {'ios': 'app_iso', 'android': 'app_android'}

    def post(self, request):
        size = request.DATA.get('size', '').strip()

        device = split_ua(request)
        device_type = device['device_type']

        if not device_type or not size:
            return Response({'ret_code': 20001, 'message': u'信息输入不完整'})

        if device_type not in ('ios', 'android') or size not in ('1', '2', '3'):
            return Response({'ret_code': 20002, 'message': u'参数不合法'})

        size = self.SIZE_MAP[size]

        activate = AppActivate.objects.filter(Q(is_used=True), Q(device=self.DEVICE_MAP[device_type]), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now()))).first()
        if activate:
            if size == 'img_one':
                img_url = activate.img_one
            elif size == 'img_two':
                img_url = activate.img_two
            elif size == 'img_three':
                img_url = activate.img_three
            else:
                img_url = ''

            if img_url:
                img_url = '{host}/media/{url}'.format(host=settings.CALLBACK_HOST, url=img_url)
                # img_url = '{host}/media/{url}'.format(host='http://192.168.1.116:8000', url=img_url)
                return Response({'ret_code': 0, 'message': 'ok', 'image': img_url})

        return Response({'ret_code': 20003, 'message': 'fail'})


