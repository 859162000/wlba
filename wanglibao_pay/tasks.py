<<<<<<< HEAD
#!/usr/bin/env python
# encoding:utf-8

"""
pay model async task
"""

from wanglibao.celery import app
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_pay.models import Card
from django.contrib.auth.models import User

@app.task
def sync_bind_card(user_id):
    """
    sync binded card from pay channel
    """
    # 查询易宝已经绑定卡
    from wanglibao_pay.yee_pay import YeeShortPay
    from wanglibao_pay.kuai_pay import KuaiShortPay

    user = User.objects.get(pk=user_id)
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
=======
from wanglibao.celery import  app
from datetime import datetime, timedelta
from django.utils.timezone import get_default_timezone
from wanglibao_pay.models import PayInfo
from wanglibao_pay.third_pay import query_trx
from wanglibao_pay.pay import PayOrder
from wanglibao_pay.exceptions import ThirdPayError

@app.task()
def sync_pay_result():
    """
    每十分钟去第三方更新当天的在5分钟之前开始且还在处理中的pay_info的处理结果
    并更新pay_info中相关记录的信息
    如果需要给用户打钱，还需要发邮件通知结算
    """
    accountant_team_email = 'jiesuan@wanglibank.com'
    admin_email = 'guoya@wanglibank.com'

    # find pay_info
        # start of today
    today = datetime.today()
    today_start = get_default_timezone().localize(datetime(today.year, today.month, today.day))
    five_min_before = get_default_timezone().localize(today - timedelta(minutes=5))
    # todo test performance
    pay_infos = PayInfo.objects.filter(type='D')\
                               .filter(channel__in=['kuaipay', 'yeepay_bind'])\
                               .filter(create_time__gte=today_start, create_time__lte=five_min_before)\
                               .filter(status='处理中').all()

    pay_order = PayOrder()

    for pay_info in pay_infos:
        pay_result = query_trx(pay_info.order_id)

        code = pay_result['code']
        message = pay_result['message']
        amount = pay_result['amount']
        last_card_no = pay_result['last_card_no']

        # check 
        if amount != pay_info.amount or last_card_no != pay_info.card_no[-4:] != last_card_no:
            return

        try:
            if code == None:
                # None, not found
                raise ThirdPayError('20333', '用户未完成交易，第三方未找到交易信息')
            else:
                # found
                if int(code) == 0:
                    pay_order.order_after_pay_succcess(amount, pay_info.order_id)
                else:
                    raise ThirdPayError(code, message)
        except ThirdPayError, error:
            pay_order.order_after_pay_error(error, pay_info.order_id)
            raise



>>>>>>> feature/query_pay
