# encoding:utf-8
from __future__ import unicode_literals
from rest_framework.response import Response
from weixin.wechatpy.exceptions import WeChatException
from functools import wraps


def weixin_api_error(f):
    @wraps(f)
    def decoration(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
        except WeChatException, e:
            return Response(e.__dict__, status=400)
        return res
    return decoration