# _*_ coding: utf-8 _*_

__author__ = 'zhanghe'


from django.contrib.auth.models import User
from marketing.models import PromotionToken
from wanglibao_sms.utils import send_validation_code
from datetime import datetime
from marketing.tops import Top


__all__ = (
    'app_share_view',
    'app_share_reg_view',
    'day_top_render',
)


def app_share_view(request, *args, **kwargs):
    identifier = request.GET.get('phone')
    reg = request.GET.get('reg')
    return {
        'identifier': identifier,
        'reg': reg
    }


def app_share_reg_view(request, *args, **kwargs):
    identifier = request.GET.get('identifier')
    friend_identifier = request.GET.get('friend_identifier')

    if friend_identifier:
        try:
            user = User.objects.get(wanglibaouserprofile__phone=friend_identifier)
            promo_token = PromotionToken.objects.get(user=user)
            invitecode = promo_token.token
        except:
            invitecode = ''
    else:
        invitecode = ''

    send_validation_code(identifier)
    return {
        'identifier': identifier,
        'invitecode': invitecode
    }


def day_top_render(request, *args, **kwargs):
    now = datetime.now()
    if now.date().__str__() <= '2015-03-23':
        return {
            "top_ten": None,
            "top_len": 0
        }

    day_tops = _get_top_records()
    return {
        "top_ten": day_tops,
        "top_len": len(day_tops)
    }


def _get_top_records(day=None):
    if day is None:
        day = datetime.now()
    top = Top(limit=10)
    return top.day_tops_activate(day)