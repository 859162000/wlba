# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from user_agents import parse

from weixin.util import getAccountInfo


def get_user_info(request, session_id):
    """
    get user's base info to php server.
    :param request:
    :param session_id:
    :return:
    userId, 用户 id.
    username, 用户手机号 .
    isDisable, 是否禁用了账户 .
    isRealname, 是否已实名
    总资产
    可用余额
    from_channel, 登录渠道 . 如 :PC
    isAdmin
    """
    user_info = dict()

    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)

    print '######'*100
    print session_id
    print request.session.session_key
    print 'ua_string = ', ua_string
    print 'user agent = ', user_agent

    if session_id == request.session.session_key:
        user = request.user
        account_info = getAccountInfo(user)
        user_info.update(userId=user.pk,
                         username=user.wanglibaouserprofile.phone,
                         realname=user.wanglibaouserprofile.name,
                         isDisable=user.wanglibaouserprofile.frozen,
                         isRealname=0,
                         total_amount=account_info['total_asset'],
                         avaliable_amount=account_info['p2p_margin'],
                         from_channel=ua_string,
                         isAdmin=user.is_superuser)

    return user_info


def get_margin_info(user_id):
    """
    :param user_id:
    :return: 用户可用余额
    """
    try:
        user = User.objects.get(pk=user_id)
        if user:
            margin = user.margin.margin
            return {'state': True, 'margin': margin}
    except Exception, e:
        print e

    return {'state': False, 'info': 'user authenticated error!'}
