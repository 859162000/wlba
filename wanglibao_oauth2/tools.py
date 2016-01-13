# encoding:utf-8

from django.utils.translation import ugettext as _
from .backends import AccessTokenBackend
from django.contrib.auth.models import User


def oauth_token_login(phone, client_id, token):
    response_data = {}
    user = User.object.filter(user__wanglibaouserprofile__phone=phone).first()
    if user:
        user = AccessTokenBackend().authenticate(token, client_id, user.id)
        if user and user.is_authenticated():
            response_data = {'code': '10000',
                             'message': _('ok')}
    else:
        response_data = {'code': '10210',
                         'message': _('Token error')}

    return response_data
