# -*- coding: utf-8 -*-

import random

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from provider.oauth2.models import AccessToken, Client
from user_agents import parse

from wanglibao import settings


def get_user_info(request, session_id):
    """
    get user's base info to php server.
    :param request:
    :param session_id:
    :return:
    userid, 用户 id.
    username, 用户手机号 .
    is_disable, 是否禁用了账户 .
    is_realname, 是否已实名
    总资产
    可用余额
    from_channel, 登录渠道 . 如 :P
    """
    user_info = dict()

    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)

    print '######'*100
    print session_id
    print request.session.session_key

    if session_id == request.session.session_key:
        user = request.user
        user_info.update(user_id=user.pk,
                         username=user.wanglibaouserprofile.name,
                         is_disable=user.wanglibaouserprofile.frozen,
                         is_realname=0,
                         total_amount=user.margin.margin,
                         avaliable_amount=user.margin.margin,
                         from_channel=ua_string)

    return user_info


def create_token(request):

    """
    根据每个渠道传来的用户名和密码去验证(或者生成)一个用户. 然后生成token返回给用户.
    :param request:
    :return:
    """
    token = request.REQUEST.get('token', '')
    username = request.REQUEST.get('username', '')
    password = request.REQUEST.get('password', '')
    expires = None
    if token:
        try:
            access_token = AccessToken.objects.get(token=token)
            user = access_token.user
            expires = access_token.expires
        except Exception, e:
            user_token = None

    # 用户名密码登录, 先确认是不是渠道用户.
    elif settings.TOKEN_CLIENTS.get(username) == password:
        try:
            # 做登录认证, 生成token
            user = authenticate(username=username, password=password)
            if not user:
                return {'state': False, 'data': 'get user error!'}
            # 根据用户名密码来获取token
        except Exception, e:
            # 注册新用户做认证.
            try:
                user = User(username=username)
                user.set_password(password)
                user.save()
                # 如果是指定字符串的认证.
                user = authenticate(username=username, password=password)
                if not user:
                    return {'state': False, 'data': 'get user error!'}
            except Exception, e:
                print 'except: {}'.format(e)
                return {'state': False, 'data': 'user authentic err: %s' % e}

    else:
        return {'state': False, 'data': 'user authenticated error!'}

    if user:
        token = AccessToken.objects.filter(user=user).last()

        try:
            user_token = token.token
        except:
            user_token = None

        # 如果token失效, 则重新生成token
        if not user_token or token.get_expire_delta() <= 0:
            user_token = generate_token()

            # client_type = 0 默认是365 有效期, 1 默认是30天有效期.
            client_type = 1
            client, status = Client.objects.get_or_create(user=user, client_type=client_type)

            AccessToken.objects.create(user=user,
                                       token=user_token,
                                       client=client,
                                       expires=expires)

        return {'state': True, 'data': user_token}


def get_token(key):
    token = AccessToken.objects.filter(token=key).first()

    return token


def get_request_token(request):
    """
    :rtype `根据渠道传的token`
    """
    request_token = request.REQUEST.get('token', '')
    token = AccessToken.objects.filter(token=request_token).first()

    return token


def check_token(token):
    """
    check token is valid or not
    :param token:
    """
    return True if AccessToken.objects.filter(token=token).exists() else False
