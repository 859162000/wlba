#!/usr/bin/env python
# encoding:utf-8
from django.http.response import HttpResponse
from rest_framework import renderers
from rest_framework.views import APIView

from wanglibao_account.auth_backends import User
from wanglibao_margin.php_utils import get_user_info, get_margin_info
from wanglibao_account import message as inside_message

class GetUserInfo(APIView):
    """
    author: Zhoudong
    http请求方式: GET  根据对应session为php获取到需要的用户信息。
    http://xxxxxx.com/php/get_user/?session_id=xilfttertn1c7581eykflhlvrm6s4peo
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        session_id = self.request.REQUEST.get('session_id')

        user_info = get_user_info(request, session_id)

        return HttpResponse(renderers.JSONRenderer().render(user_info, 'application/json'))


class GetMarginInfo(APIView):
    """
    author: Zhoudong
    http请求方式: GET  根据用户ID 得到用户可用余额。
    http://xxxxxx.com/php/margin/?user_id=11111
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        user_id = self.request.REQUEST.get('userId')

        margin = get_margin_info(user_id)

        return HttpResponse(renderers.JSONRenderer().render(margin, 'application/json'))


class SendInsideMessage(APIView):
    """
    author: Zhoudong
    http请求方式: GET  根据用户ID 得到用户可用余额。
    http://xxxxxx.com/php/margin/?user_id=11111
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        user_id = self.request.POST.get('userId')
        # useless argument.
        # msg_type = self.request.POST.get('msgType')
        title = self.request.POST.get('title')
        content = self.request.POST.get('content')

        try:
            inside_message.send_one.apply_async(kwargs={
                "user_id": user_id,
                "title": title,
                "content": content,
                "mtype": "activity"
            })
            ret = {'status': 1, 'message': 'Succeed'}
        except Exception, e:
            ret = {'status': 0, 'message': e}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class CheckTradePassword(APIView):
    """
    author: Zhoudong
    http请求方式: GET  根据用户ID 得到用户可用余额。
    http://xxxxxx.com/php/margin/?user_id=11111
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        user_id = self.request.POST.get('userId')
        trade_password = self.request.POST.get('password')

        try:
            user = User.objects.get(pk=user_id)
            if trade_password == user.wanglibaouserprofile.trade_pwd:
                ret = {'status': 1, 'message': 'Succeed'}
            else:
                ret = {'status': 0, 'message': 'password error!'}
        except Exception, e:
            ret = {'status': 0, 'message': e}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
