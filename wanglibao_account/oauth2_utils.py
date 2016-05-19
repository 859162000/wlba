# -*- coding: utf-8 -*-

import random

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from provider.oauth2.models import AccessToken, Client
from wanglibao import settings

UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')


def generate_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    """
    默认有 token 字符串生成方法.
    Generates a non-guessable OAuth token

    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))


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
            # 波波说不要自己建用户. 手动建.#########
            # 注册新用户做认证.
            # try:
            #     user = User(username=username)
            #     user.set_password(password)
            #     user.save()
            #     TODO: wanglibaouserprofile 表增加用户.
            #     # 如果是指定字符串的认证.
            #     user = authenticate(username=username, password=password)
            #     if not user:
            #         return {'state': False, 'data': 'get user error!'}
            # except Exception, e:
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
