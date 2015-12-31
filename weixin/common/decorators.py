# encoding:utf-8
from __future__ import unicode_literals
from functools import wraps

from rest_framework.response import Response
from django.http import HttpResponseRedirect

from wechatpy.exceptions import WeChatException
from weixin.models import WeixinAccounts
from wanglibao_pay.models import Card
from django.db.models import Q
import logging
logger = logging.getLogger("weixin")
def weixin_api_error(f):
    @wraps(f)
    def decoration(obj, request, *args, **kwargs):
        try:
            res = f(obj, request, *args, **kwargs)
        except WeChatException, e:
            res = e.__dict__
            # 40014 不合法的access_token，请开发者认真比对access_token的有效性（如是否过期），或查看是否正在为恰当的公众号调用接口
            # 42001: 'access_token超时，请检查access_token的有效期，请参考基础支持-获取access_token中，对access_token的详细机制说明',
            # 42002: 'refresh_token超时',
            # 42003: 'oauth_code超时',
            errcode = res.get('errcode')
            current_account = WeixinAccounts.get(request.session.get('account_key'))

            if errcode == 40014 or errcode == 43001 or errcode == 40001:
                current_account.db_account.update_access_token()
                logger.debug("------------------------refreshed access_token in weixin_api_error")
            elif errcode == 42002:
                pass
            elif errcode == 42003:
                pass
            try:
                logger.debug("------------------------wexinerror---%s--%s"%(errcode, request.get_full_path()))
            except:
                pass
            return Response({'errcode':e.errcode, 'errmsg':e.errmsg}, status=400)
        return res
    return decoration

def is_check_id_verify(is_check):
    def check_id_Verify(f):
        @wraps(f)
        def check(self, request, *args, **kwargs):
            if is_check:

                wanglibaoprofile = self.request.user.wanglibaouserprofile
                if not wanglibaoprofile.id_is_valid:
                    return HttpResponseRedirect("/weixin/sub_regist_first/")

                cards = Card.objects.filter(user=self.request.user).filter(Q(is_bind_huifu=True)|Q(is_bind_kuai=True)|Q(is_bind_yee=True))# Q(is_bind_huifu=True)|)
                if not cards.exists():
                    return HttpResponseRedirect("/weixin/sub_regist_second/")
            res = f(self, request, *args, **kwargs)
            return res
        return check
    return check_id_Verify

