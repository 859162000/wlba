# encoding:utf-8
from django.forms import model_to_dict
from order.models import Order
from order.utils import OrderHelper

from wanglibao.celery import app
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_p2p.models import P2PProduct, P2PRecord, Earning
from wanglibao_account.models import Binding
from wanglibao_p2p.trade import P2POperator
from django.db.models import Sum, connection
from datetime import datetime
from django.contrib.auth.models import User
import os
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages



@app.task
def p2p_watchdog():
    P2POperator().watchdog()


@app.task
def process_paid_product(product_id):
    P2POperator.preprocess_for_settle(P2PProduct.objects.get(pk=product_id))

@app.task
def build_earning(product_id):

    # command = 'touch ~/workspace/%s.txt' % 'test'
    # os.system(command)

    p2p = P2PProduct.objects.select_related('activity__rule').get(pk=product_id)

    #按用户汇总某个标的收益
    earning = P2PRecord.objects.values('user').annotate(sum_amount=Sum('amount')).filter(product=p2p, catalog=u'申购')

    phone_list = []
    rule = p2p.activity.rule



    #把收益数据插入earning表内
    for obj in earning:

        bind = Binding.objects.get(user_id=obj.get('user'))
        if bind and bind.isvip:
            earning = Earning()
            amount = rule.get_earning(obj.get('sum_amount'), p2p.period, rule.rule_type)
            earning.amount = amount
            earning.type = 'D'
            earning.product = p2p
            user = User.objects.get(pk=obj.get('user'))
            order = OrderHelper.place_order(user, Order.ACTIVITY, u"活动赠送",
                                            earning = model_to_dict(earning))
            earning.order = order

            keeper = MarginKeeper(user, order.pk)

            #赠送活动描述
            desc = u'%s,%s赠送%s%s' % (p2p.name, p2p.activity.name, p2p.activity.rule.rule_amount*100, '%')
            earning.margin_record = keeper.deposit(amount,description=desc)
            earning.user = user
            earning.save()

            #发送活动赠送短信
            send_messages.apply_async(kwargs={
                            "phones": user.wanglibaouserprofile.phone,
                            "messages": [messages.earning_message(p2p.name, p2p.activity.name, amount)]
                        })
