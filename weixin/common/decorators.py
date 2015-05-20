# encoding:utf-8
from __future__ import unicode_literals
from rest_framework.response import Response
from weixin.wechatpy.exceptions import WeChatException
from functools import wraps
from weixin.models import Account


def weixin_api_error(f):
    @wraps(f)
    def decoration(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
        except WeChatException, e:
            res = e.__dict__
            # 40014 不合法的access_token，请开发者认真比对access_token的有效性（如是否过期），或查看是否正在为恰当的公众号调用接口
            # 42001: 'access_token超时，请检查access_token的有效期，请参考基础支持-获取access_token中，对access_token的详细机制说明',
            # 42002: 'refresh_token超时',
            # 42003: 'oauth_code超时',
            errcode = res.get('errcode')
            current_account = Account.objects.first()
            if errcode == 40014 or errcode == 43001:
                current_account.update_access_token()
            elif errcode == 42002:
                pass
            elif errcode == 42003:
                pass

            return Response(res, status=400)
        return res
    return decoration
