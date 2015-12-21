# -*- coding: utf-8 -*-
import requests
import simplejson
from django.db import transaction

from wanglibao import settings
from wanglibao.celery import app
from django.contrib.auth.models import User

from wanglibao_margin.models import MonthProduct, AssignmentOfClaims
from wanglibao_margin.php_utils import PhpMarginKeeper


def save_to_sqs(url, data):

    response = requests.post(url, data)
    print response.headers
    return response


@app.task
def buy_month_product(trade_id, user_id, product_id, token, amount, amount_source, red_packet, red_packet_type):

    ret = dict()

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
    data = dict()
    data.update(tag='purchaseYueLiBao')
    data.update(data=ret)

    data = simplejson.dumps(data)
    url = settings.PHP_SQS_HOST
    ret = save_to_sqs(url, data)

    print ret.text


@app.task
def assignment_buy(buyer_id, seller_id, product_id, buy_order_id, sell_order_id, buyer_token, seller_token,
                   fee, premium_fee, trading_fee, buy_price, sell_price, buy_price_source, sell_price_source):
    """

    :param buyer_id:
    :param seller_id:
    :param product_id:
    :param buy_order_id:
    :param sell_order_id:
    :param buyer_token:
    :param seller_token:
    :param fee:
    :param premium_fee:
    :param trading_fee:
    :param buy_price:
    :param sell_price:
    :param buy_price_source:
    :param sell_price_source:
    :return:
    """
    ret = dict()

    try:
        buyer = User.objects.get(pk=buyer_id)
        seller = User.objects.get(pk=seller_id)
        assignment, status = AssignmentOfClaims.objects.get_or_create(
            product_id=product_id,
            buyer=buyer,
            seller=seller,
            buyer_order_id=buy_order_id,
            seller_order_id=sell_order_id,
            buyer_token=buyer_token,
            seller_token=seller_token,
            fee=fee,
            premium_fee=premium_fee,
            trading_fee=trading_fee,
            buy_price=buy_price,
            sell_price=sell_price,
            buy_price_source=buy_price_source,
            sell_price_source=sell_price_source
        )
        # 状态成功, 对买家扣款, 卖家回款.
        if status:
            try:
                with transaction.atomic(savepoint=True):
                    # status == 0 加钱, 其他减钱. 这直接对买家余额减钱, 卖家余额加钱
                    buyer_keeper = PhpMarginKeeper(buyer, )
                    seller_keeper = PhpMarginKeeper(seller, )
                    buyer_keeper.margin_process(buyer, 1, buy_price, description=u'', catalog=u"买债转")
                    seller_keeper.margin_process(seller, 0, sell_price, description=u'', catalog=u"卖债转")

                    # 如果加减钱成功后, 更新债转的表的状态为成功
                    assignment.status = True
                    assignment.save()
                    ret.update(status=1,
                               buyer_token=buyer_token,
                               seller_token=seller_token,
                               msg='success')
            except Exception, e:
                ret.update(status=0,
                           msg=str(e))
        else:
            ret.update(status=0,
                       msg='save error')
    except Exception, e:
        ret.update(status=0,
                   msg=str(e))

    # 写入 sqs
    data = dict()
    data.update(tag='purchaseZhaiZhuan')
    data.update(data=ret)
    data = simplejson.dumps(data)
    url = settings.PHP_SQS_HOST
    ret = save_to_sqs(url, data)

    print ret.text
