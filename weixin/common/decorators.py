# encoding:utf-8
from __future__ import unicode_literals
from functools import wraps

from rest_framework.response import Response
from django.http import HttpResponseRedirect
from functools import wraps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import available_attrs
from django.utils.encoding import force_str
from django.utils.six.moves.urllib.parse import urlparse
from django.shortcuts import resolve_url
from wechatpy.exceptions import WeChatException
from weixin.models import WeixinAccounts, WeixinUser
import logging
logger = logging.getLogger("weixin")

def fwh_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def handle_user(request):
        user = request.user
        openid = request.session.get('openid')
        if user.is_authenticated() and openid:
            w_user = WeixinUser.objects.filter(openid=openid, user=user).first()
            return (w_user is not None)
        return False
    actual_decorator = user_passes_test(
        handle_user,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            # urlparse chokes on lazy objects in Python 3, force to str
            resolved_login_url = force_str(
                resolve_url(login_url or settings.LOGIN_URL))
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator


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

                # cards = Card.objects.filter(user=self.request.user).filter(Q(is_bind_huifu=True)|Q(is_bind_kuai=True)|Q(is_bind_yee=True))# Q(is_bind_huifu=True)|)
                # if not cards.exists():
                #     return HttpResponseRedirect("/weixin/sub_regist_second/")
            res = f(self, request, *args, **kwargs)
            return res
        return check
    return check_id_Verify

