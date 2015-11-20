#!/usr/bin/env python
# encoding:utf-8
from django.http.response import HttpResponse
from rest_framework import renderers
from rest_framework.views import APIView

from wanglibao import settings
from wanglibao_margin.php_utils import get_user_info


class GetUserInfo(APIView):
    """
    author: Zhoudong
    http请求方式: GET  获取请求当天发布并且当天结束的项目（防止漏掉秒杀标）及系统中所有未完成（预投标，投标中）的项目列表。
    http://xxxxxx.com/getList
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        session_id = self.request.REQUEST.get('session_id')

        user_info = get_user_info(request, session_id)

        return HttpResponse(renderers.JSONRenderer().render(user_info, 'application/json'))
