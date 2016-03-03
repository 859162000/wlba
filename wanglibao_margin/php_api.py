#!/usr/bin/env python
# encoding:utf-8

from django.http.response import HttpResponse
from rest_framework import renderers
from rest_framework.views import APIView

from wanglibao_margin.php_utils import send_redpacks


class SendRedPacks(APIView):
    """
    http请求方式: post
    http://xxxxxx.com/php/redpacks/send/
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()

    def post(self, request):

        redpack_id = self.request.REQUEST.get('redpack_id')
        user_ids = self.request.REQUEST.get('userIds').split(',')

        if redpack_id and user_ids:
            ret = send_redpacks(redpack_id, user_ids)

        else:
            ret = {'status': 0,
                   'msg': 'args error!'}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
