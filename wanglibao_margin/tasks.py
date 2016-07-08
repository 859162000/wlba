# -*- coding: utf-8 -*-
import logging
import urllib2

import requests
import simplejson
from django.contrib.auth.models import User
from django.db import transaction

from marketing import tools
from order.utils import OrderHelper
from wanglibao import settings
from wanglibao.celery import app
from wanglibao_account.cooperation import CoopRegister

from wanglibao_margin.models import MonthProduct, AssignmentOfClaims
from wanglibao_margin.php_utils import PhpMarginKeeper, php_redpack_consume
from wanglibao_redpack.models import RedPackRecord
from wanglibao_reward.views import RuiKeDistributer

logger = logging.getLogger('wanglibao_margin')


def save_to_sqs(url, data):

    response = requests.post(url, data)
    print response.headers
    return response


@app.task
def buy_month_product(token=None, red_packet_id=None, amount_source=None, user=None, device=None, period=0):
    """
    对这个购买的月利宝记录进行扣款冻结操作.
    :param token: month_product's unique token.
    ###  :param product: pass a month_product object error!
    amount_source: 购买的总金额
    ###### 以下  如果是 amount 是 优惠后的金额
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
        # 未被取消的订单才可以扣款
        if not product.cancel_status:
            # 状态成功, 对买家扣款, 加入冻结资金
            try:
                with transaction.atomic(savepoint=True):
                    buyer_keeper = PhpMarginKeeper(product.user, product.product_id)

                    user = User.objects.filter(pk=user).first()

                    # update by lili 2016-06-14
                    # 如果使用红包的话,需要先将红包的钱判断正确后存入用户账户,然后再去检测购买金额和余额
                    # 如果使用红包的话, 增加红包使用记录
                    if red_packet_id and int(red_packet_id) > 0:
                        logger.info('buy_month_product token = {} used with red_pack_id = {}'.format(token, red_packet_id))
                        redpack = RedPackRecord.objects.filter(pk=red_packet_id).first()
                        redpack_order_id = OrderHelper.place_order(user, order_type=u'优惠券消费', redpack=redpack.id,
                                                                   product_id=product.product_id, status=u'新建').id
                        result = php_redpack_consume(red_packet_id, amount_source, user, product.id,
                                                     device['device_type'], product.product_id)
                        if result['ret_code'] != 0:
                            raise Exception, result['message']
                        if result['rtype'] != 'interest_coupon':
                            red_record = buyer_keeper.redpack_deposit(
                                result['deduct'], u"购买月利宝抵扣%s元" % result['deduct'],
                                order_id=redpack_order_id, savepoint=False)

                    buyer_keeper.php_freeze(amount_source, description=u'月利宝购买冻结')
                    product.trade_status = 'PAID'
                    product.save()
                    ret.update(status=1,
                               token=token,
                               msg='success')

                    try:
                        tools.decide_first.apply_async(kwargs={"user_id": user.id, "amount": amount_source,
                                                               "device": device, "order_id": product.id,
                                                               "product_id": product.id, "is_full": False,
                                                               "product_balance_after": 0, "ylb_period": int(period)},
                                                       queue='celery_ylb')

                    except Exception, e:
                        logger.debug('tools.decide_first.apply_async failed with = {} !!!'.format(e.message))

                    # 模拟一个request
                    request = urllib2.Request("")
                    try:
                        CoopRegister(request).process_for_purchase_yuelibao(user, product.id)
                    except Exception, e:
                        logger.debug(u"=遍历渠道= CoopRegister.process_for_purchase Except:{}".format(e))

                    # ruike qudao
                    try:
                        kargs = {
                            'amount': amount_source,
                            'order_id': product.id,
                            'user': user,
                            'request': request,
                            'product': None,
                        }
                        ruike_obj = RuiKeDistributer(request, kargs)
                        ruike_obj.distribute()
                    except Exception, e:
                        logger.debug(u'ruike call failed with : {}'.format(e.message))

            except Exception, e:
                logger.exception("buy_month_product failed:")
                logger.debug('buy_month_product failed with exception: {}, red_pack_id = {}'.format(str(e), red_packet_id))
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

    logger.info('in buy_month_product, token = {}, freeze = {}'.format(token, product.amount_source))
    logger.info('save to sqs! args = {}, return = {}'.format(args, res))


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

                # 买家流水
                buyer_ret = buyer_keeper.margin_process(
                          assignment.buyer, 1, assignment.buy_price, description=u'买债转', catalog=u"投资")
                if buyer_ret:
                    # 卖家流水
                    seller_keeper.margin_process(
                        assignment.seller, 0, assignment.buy_price, description=u'卖债转', catalog=u"转让回款")
                    # 卖家流水增加一条, 先加买家的钱, 再减去平台手续费
                    seller_keeper.margin_process(
                        assignment.seller, 1, assignment.fee, description=u'债转平台手续费', catalog=u"转让手续费")

                    # 如果加减钱成功后, 更新债转的表的状态为成功
                    assignment.trade_status = 'PAID'
                    assignment.save()
                    ret.update(status=1,
                               buyToken=assignment.buyer_token,
                               sellToken=assignment.seller_token,
                               msg='success')
                else:
                    ret.update(status=0,
                               buyToken=assignment.buyer_token,
                               sellToken=assignment.seller_token,
                               msg=u'用户余额不足')
        except Exception, e:
            logger.debug('buy assignment product failed with exception: {}'.format(str(e)))
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

    logger.info('in buy zhaizhuan, buyer_token = {}, seller_token = {}'.format(buyer_token, seller_token))
    logger.info('save to sqs! args = {}, return = {}'.format(data, ret))
