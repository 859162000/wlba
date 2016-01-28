#!/usr/bin/env python
# encoding:utf-8

"""
pay model async task
"""

from wanglibao.celery import app
from wanglibao_pay.yee_pay import YeeShortPay
from wanglibao_pay.kuai_pay import KuaiShortPay
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_pay.models import Card

@app.task
def sync_bind_card(user_id):
    """
    sync binded card from pay channel
    """
    # 查询易宝已经绑定卡
    user = WanglibaoUserProfile.objects.get(pk=user_id)
    res = YeeShortPay().bind_card_query(user=user)
    if res['ret_code'] not in (0, 20011):
        return res
    if 'data' in res and 'cardlist' in res['data']:
        yee_card_no_list = []
    for car in res['data']['cardlist']:
        card = Card.objects.filter(user=user, no__startswith=car['card_top'],
                                   no__endswith=car['card_last']).first()
        if card:
            yee_card_no_list.append(card.no)
    if yee_card_no_list:
        Card.objects.filter(user=user, no__in=yee_card_no_list).update(is_bind_yee=True)
        Card.objects.filter(user=user).exclude(no__in=yee_card_no_list).update(is_bind_yee=False)

    # 查询块钱已经绑定卡
    res = KuaiShortPay().query_bind_new(user.id)
    if res['ret_code'] != 0:
        return res
    if 'cards' in res:
        kuai_card_no_list = []
    for car in res['cards']:
        card = Card.objects.filter(user=user, no__startswith=car[:6], no__endswith=car[-4:]).first()
        if card:
            kuai_card_no_list.append(card.no)
    if kuai_card_no_list:
        Card.objects.filter(user=user, no__in=kuai_card_no_list).update(is_bind_kuai=True)
        Card.objects.filter(user=user).exclude(no__in=kuai_card_no_list).update(is_bind_kuai=False)
