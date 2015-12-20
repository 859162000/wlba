# -*- coding: utf-8 -*-
import requests
import simplejson
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import renderers

from wanglibao import settings
from wanglibao.celery import app
from django.contrib.auth.models import User

from wanglibao_margin.models import MonthProduct, MarginRecord
from wanglibao_margin.php_utils import PhpMarginKeeper, calc_php_commission


def save_to_sqs(url, data):

    response = requests.post(url, data)
    print response.headers
    return response


@app.task
def buy_month_product(trade_id, user_id, product_id, token, amount, amount_source, red_packet, red_packet_type):

    ret = dict()
    data = dict()

    data.update(tag='purchaseYueLiBao')

    try:
        user = User.objects.get(pk=user_id)
        assignment, status = MonthProduct.objects.get_or_create(
            user=user,
            product_id=product_id,
            trade_id=trade_id,
            token=token,
            amount=amount,
            amount_source=amount_source,
            red_packet=red_packet,
            red_packet_type=red_packet_type,
        )
        # 状态成功, 对买家扣款, 加入冻结资金
        if status:
            print 'sss status' * 100
            try:
                buyer_keeper = PhpMarginKeeper(user, product_id)
                buyer_keeper.freeze(amount, description='')
                assignment.pay_status = True
                assignment.save()
                ret.update(status=1,
                           token=token,
                           msg='success')
            except Exception, e:
                ret.update(status=0,
                           token=token,
                           msg=str(e))
        else:
            if assignment.pay_status:
                ret.update(status=1,
                           token=token,
                           msg='already saved!')
            else:
                ret.update(status=0,
                           token=token,
                           msg='pay failed!')

    except Exception, e:
        ret.update(status=0,
                   token=token,
                   msg=str(e))

    # 写入 sqs
    data.update(data=ret)
    data = simplejson.dumps(data)
    url = settings.PHP_SQS_HOST + '?opt=put&name=interfaces'
    ret = save_to_sqs(url, data)

    print ret.text


@app.task
def month_product_buy_fail(user_id, token):

    ret = dict()

    user = User.objects.get(pk=user_id)
    product = MonthProduct.objects.filter(token=token).first()

    if not product:
        ret.update(status=2, msg='success', token=token)
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
    if product.cancel_status:
        ret.update(status=1, msg='success', token=token)
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

    try:
        with transaction.atomic(savepoint=True):
            product_id = product.product_id
            buyer_keeper = PhpMarginKeeper(user, product_id)
            record = buyer_keeper.yue_cancel(user, product.amount)

            if record:
                # 状态置为已退款, 这个记录丢弃
                product.cancel_status = True
                product.save()

            ret.update(status=1,
                       msg='success',
                       token=token)

    except Exception, e:
        ret.update(status=0,
                   msg=str(e),
                   token=token)
    # 写入 sqs
    data = dict()
    data.update(data=ret)
    data = simplejson.dumps(data)
    url = settings.PHP_SQS_HOST + '?opt=put&name=interfaces'
    ret = save_to_sqs(url, data)

    print ret


@app.task
def month_product_check(product_id):

    ret = dict()

    try:
        with transaction.atomic(savepoint=True):
            month_products = MonthProduct.objects.filter(
                product_id=product_id, cancel_status=False, pay_status=False)

            for product in month_products:
                # 已支付, 直接返回成功
                if not product.pay_status:
                    user = product.user
                    product_id = product.product_id
                    buyer_keeper = PhpMarginKeeper(user, product_id)
                    trace = buyer_keeper.settle(product.amount, description='')
                    if trace:
                        product.pay_status = True
                        product.save()

            # 进行全民淘金数据写入
            calc_php_commission(product_id)

            ret.update(status=1,
                       msg='success',
                       product_id=product_id)
    except Exception, e:
        ret.update(status=0,
                   msg=str(e),
                   product_id=product_id)


@app.task
def month_product_cancel(tokens):

    ret = dict()
    msg_list = list()

    try:
        with transaction.atomic(savepoint=True):
            month_products = MonthProduct.objects.filter(token__in=tokens)
            for product in month_products:
                user = product.user
                product_id = product.product_id
                buyer_keeper = PhpMarginKeeper(user, product_id)
                record = buyer_keeper.unfreeze(product.amount, description='')

                # 状态置为已退款, 这个记录丢弃
                product.cancel_status = True
                product.save()

                status = 1 if record else 0
                msg_list.append({'token': product.token, 'status': status})

        ret.update(status=1,
                   msg=msg_list)
    except Exception, e:
        ret.update(status=0,
                   msg=str(e))

    # 写入 sqs
    data = dict()
    data.update(data=ret)
    data = simplejson.dumps(data)
    url = settings.PHP_SQS_HOST + '?opt=put&name=interfaces'
    ret = save_to_sqs(url, data)

    print ret


@app.task
def month_product_refund(args):
    """

    :param args:
    :return:
    """
    ret = dict()
    msg_list = list()

    try:
        with transaction.atomic(savepoint=True):
            for arg in eval(args):
                user = User.objects.get(pk=arg['userId'])

                margin_record = MarginRecord.objects.filter(
                    # (Q(catalog=u'月礼包本金入账') | Q(catalog=u'债转本金入账')) &
                    (Q(catalog=u'\u6708\u5229\u5b9d\u672c\u91d1\u5165\u8d26') |
                     Q(catalog=u'\u503a\u8f6c\u672c\u91d1\u5165\u8d26')) &
                    Q(order_id=arg['refundId']) & Q(user=user)
                ).first()

                if margin_record:
                    msg_list.append({'refundId': arg['refundId'], 'status': 1})

                else:
                    buyer_keeper = PhpMarginKeeper(user, arg['refundId'])

                    try:
                        buyer_keeper.php_amortize_detail(
                            arg['tradeType'], arg['principal'], arg['interest'], 0, arg['increase'],
                            arg['plusInterest'], arg['refundId']
                        )
                        msg_list.append({'refundId': arg['refundId'], 'status': 1})

                    except Exception, e:
                        print e

            ret.update(status=1,
                       msg=msg_list)

    except Exception, e:
        ret.update(status=0,
                   msg=str(e))

    # 写入 sqs
    data = dict()
    data.update(data=ret)
    data = simplejson.dumps(data)
    url = settings.PHP_SQS_HOST + '?opt=put&name=interfaces'
    ret = save_to_sqs(url, data)

    print ret
