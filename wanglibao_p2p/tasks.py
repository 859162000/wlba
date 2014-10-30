# encoding:utf-8

from wanglibao.celery import app
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_account.models import Binding
from wanglibao_p2p.trade import P2POperator
from django.db.models import Sum, connection
from datetime import datetime


@app.task
def p2p_watchdog():
    P2POperator().watchdog()


@app.task
def process_paid_product(product_id):
    P2POperator.preprocess_for_settle(P2PProduct.objects.get(pk=product_id))

@app.task
def build_earning(product_id):

    p2p = P2PProduct.objects.select_related('activity__rule').get(pk=product_id)

    #按用户汇总某个标的收益
    earning = P2PRecord.objects.values('user').annotate(sum_amount=Sum('amount')).filter(product=p2p, catalog=u'申购')

    value_list = []
    rule = p2p.activity.rule

    #把收益数据插入earning表内
    for obj in earning:
        bind = Binding.objects.get(user=obj.get('user'))
        if bind and bind.isvip:
            amount = rule.get_earning(obj.get('sum_amount'), p2p.period, rule.rule_type)
            value_list.append(((p2p.pk, obj.get('user'), amount, datetime.now(), 0)))


    cursor = connection.cursor()
    cursor.executemany("""insert into wanglibao_p2p_earning (product_id, user_id,amount, create_time,paid) values (%s, %s, %s, %s, %s)""", value_list)
