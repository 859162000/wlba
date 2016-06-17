#!/usr/bin/env python
# encoding: utf-8

import json
import logging
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from .models import CallbackRecord

logger = logging.getLogger(__name__)


def product_period_to_days(pay_method, period):
    # 根据支付方式判定标周期的单位（天/月）,如果是单位为月则转换为天
    pay_method_for_months = (u'等额本息', u'按月付息', u'到期还本付息')
    if pay_method in pay_method_for_months:
        period = relativedelta(months=period).days

    return period


def get_product_period_type(pay_method):
    if pay_method in [u'等额本息', u'按月付息', u'到期还本付息']:
        period_type = 1
    else:
        period_type = 2

    return period_type


def get_bajinshe_access_token(order_id):
    access_token = None
    message = None

    coop_access_token_url = settings.BAJINSHE_ACCESS_TOKEN_URL

    data = {
        'platform': settings.BAJINSHE_COOP_ID,
        'key': settings.BAJINSHE_COOP_KEY,
        'order_id': order_id,
    }

    headers = {
       'Content-Type': 'application/json',
    }

    res = requests.post(url=coop_access_token_url, data=json.dumps(data), headers=headers)
    logger.info("bajinshe access token url [%s]" % res.url)
    logger.info("bajinshe access token request data [%s]" % data)
    res_status_code = res.status_code
    if res_status_code == 200:
        res_data = res.json()
        logger.info("get_bajinshe_access_token return: %s" % res_data)
        if res_data['code'] == '10000':
            access_token = res_data.get('access_token', None)
            message = 'success'
        else:
            logger.info("bajinshe access token faild return %s" % res_data)
    else:
        message = 'bad request %s' % res_status_code
        logger.info("bajinshe access token connect faild with status code[%s]" % res_status_code)
        logger.info(res.text)

    logger.info("get_bajinshe_access_token process result: %s" % message)
    return access_token


def save_to_callback_record(data, channel):
    """
    渠道用户回调记录
    """
    data['callback_to'] = channel
    data['request_data'] = json.dumps(data['request_data'])
    request_headers = data.get('request_headers', None)
    if request_headers:
        data['request_headers'] = json.dumps(request_headers)

    call_back_record = CallbackRecord()
    for k, v in data.iteritems():
        setattr(call_back_record, k, v)

    call_back_record.save()
