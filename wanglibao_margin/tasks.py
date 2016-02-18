# -*- coding: utf-8 -*-
import requests
import simplejson
from django.contrib.auth.models import User
from django.db import transaction

from order.utils import OrderHelper
from wanglibao import settings
from wanglibao.celery import app

from wanglibao_margin.models import MonthProduct, AssignmentOfClaims
from wanglibao_margin.php_utils import PhpMarginKeeper, php_redpack_consume
from wanglibao_redpack.models import RedPackRecord


def save_to_sqs(url, data):

    response = requests.post(url, data)
    print response.headers
    return response


@app.task
def buy_month_product(token=None, red_packet_id=None, amount=None, user=None, device_type=None):
    """
    对这个购买的月利宝记录进行扣款冻结操作.
    :param token: month_product's unique token.
    ###  :param product: pass a month_product object error!
    :return:
    """
    product = MonthProduct.objects.filter(token=token).first()
    if not product:
        return

    ret = dict()

    if product.trade_status != 'NEW':
        ret.update(status=1,
                   token=product.token,
                   msg='already saved!')
    else:
        # 状态成功, 对买家扣款, 加入冻结资金
        try:
            with transaction.atomic(savepoint=True):
                buyer_keeper = PhpMarginKeeper(product.user, product.product_id)
                buyer_keeper.freeze(product.amount, description='')
                product.trade_status = 'PAID'
                product.save()
                ret.update(status=1,
                           token=product.token,
                           msg='success')

                # 如果使用红包的话, 增加红包使用记录
                if red_packet_id and int(red_packet_id) > 0:
                    redpack = RedPackRecord.objects.filter(pk=red_packet_id).first()
                    user = User.objects.filter(pk=user).first()
                    redpack_order_id = OrderHelper.place_order(user, order_type=u'优惠券消费', redpack=redpack.id,
                                                               product_id=product.product_id, status=u'新建').id
                    result = php_redpack_consume(red_packet_id, amount, user, product.id, device_type, product.product_id)
                    if result['ret_code'] != 0:
                        raise Exception, result['message']
                    if result['rtype'] != 'interest_coupon':
                        red_record = buyer_keeper.redpack_deposit(result['deduct'], u"购买月利宝抵扣%s元" % result['deduct'],
                                                                  order_id=redpack_order_id, savepoint=False)

        except Exception, e:
            f = open('.stdout.txt', 'a+')
            print >> f, 'buy month product failed with error:'
            print >> f, 'e = {}'.format(e)
            print >>f, 'redpack id = {}'.format(red_packet_id)
            f.close()
            product.trade_status = 'FAILED'
            product.save()
            ret.update(status=0,
                       token=product.token,
                       msg='pay failed!' + str(e))

    # 写入 sqs
    args_data = dict()
    args_data.update(tag='purchaseYueLiBao')
    args_data.update(data=ret)

    args = simplejson.dumps(args_data)
    request_url = settings.PHP_SQS_HOST
    res = save_to_sqs(request_url, args)

    print res.text


@app.task
def assignment_buy(buyer_token=None, seller_token=None):
    """
    :param buyer_token:
    :param seller_token:
    :return:
    """
    assignment = AssignmentOfClaims.objects.filter(buyer_token=buyer_token, seller_token=seller_token).first()
    if not assignment:
        return

    ret = dict()

    if assignment.trade_status != 'NEW':
        ret.update(status=1,
                   buyToken=assignment.buyer_token,
                   sellToken=assignment.seller_token,
                   msg='already saved!')

    else:
        # 状态成功, 对买家扣款, 卖家回款.
        try:
            with transaction.atomic(savepoint=True):
                # status == 0 加钱, 其他减钱. 这直接对买家余额减钱, 卖家余额加钱
                buyer_keeper = PhpMarginKeeper(assignment.buyer, )
                seller_keeper = PhpMarginKeeper(assignment.seller, )
                buyer_keeper.margin_process(
                    assignment.buyer, 1, assignment.buy_price, description=u'', catalog=u"买债转")
                seller_keeper.margin_process(
                    assignment.seller, 0, assignment.sell_price, description=u'', catalog=u"卖债转")

                # 如果加减钱成功后, 更新债转的表的状态为成功
                assignment.trade_status = 'PAID'
                assignment.save()
                ret.update(status=1,
                           buyToken=assignment.buyer_token,
                           sellToken=assignment.seller_token,
                           msg='success')
        except Exception, e:
            assignment.trade_status = 'FAILED'
            ret.update(status=0,
                       buyToken=assignment.buyer_token,
                       sellToken=assignment.seller_token,
                       msg=str(e))

    # 写入 sqs
    data = dict()
    data.update(tag='purchaseZhaiZhuan')
    data.update(data=ret)
    data = simplejson.dumps(data)
    url = settings.PHP_SQS_HOST
    ret = save_to_sqs(url, data)

    print ret.text
