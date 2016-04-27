#!/usr/bin/env python
# encoding:utf-8

import logging
from wanglibao.celery import app
from django.contrib.auth.models import User
from wanglibao_activity.backends import check_activity
import datetime

logger = logging.getLogger(__name__)


@app.task
def check_activity(user_id, trigger_node, device_type, **kwargs):
    """
    检测活动
    :param user_id, 用户id
    :param trigger_node, 活动触发节点
    :param device_type, 设备类型 'pc','android', 'ios'
    :param kwargs, amount=0, product_id=0, order_id=0, is_full=False, is_first_bind=False
    """

    if not user_id or not trigger_node:
        logger.debug(">>>>> not user_id: [{}] or not trigger_node: [{}]".format(user_id, trigger_node))
        return

    if not device_type:
        device_type = 'pc'

    user = User.objects.filter(pk=user_id).first()
    if user:
        amount = kwargs['amount'] or 0
        product_id = kwargs['product_id'] or 0
        order_id = kwargs['order_id'] or 0
        is_full = kwargs['is_full'] or False
        is_first_bind = kwargs['is_first_bind'] or False

        try:
            check_activity(user, trigger_node, device_type, amount=amount, product_id=product_id, order_id=order_id,
                           is_full=is_full, is_first_bind=is_first_bind)
        except Exception:
            logger.exception(">>>>> check activity err")
            logger.debug(">>>>> err_date:[{}], user:[{}], trigger_node:[{}], device_type:[{}], "
                         "amount:[{}], product: [{}], order:[{}], is_full:[{}], "
                         "is_first_bind:[{}]".format(datetime.datetime.now(), user_id, trigger_node, device_type,
                                                     amount, product_id, order_id, is_full, is_first_bind))
    else:
        logger.debug(">>>>> start check activity, user not exist, param user_id: %s" % user_id)
        return
