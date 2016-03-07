#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import requests
import urllib
from decimal import Decimal
from wanglibao.celery import app
from wanglibao import settings
from wanglibao_pay.models import PayInfo
from wanglibao_margin.models import MarginRecord
from .utils import get_bajinshe_access_token
from wanglibao_account.tools import get_tid_for_coop, get_user_phone_for_coop
from django.utils import timezone

logger = logging.getLogger(__name__)


def callback(url, params, channel_name):
    logger.info("Enter %s_callback task===>>>"%channel_name)
    try:
        params = urllib.urlencode(params)
        logger.info(params)
        ret = requests.get(url, params=params)
        logger.info('%s callback url: %s'%(channel_name,ret.url))
        logger.info('%s callback return: %s' % (channel_name, ret.text))
        return ret
    except Exception, e:
        logger.info(" {'%s callback':'failed to connect'} "%channel_name)
        logger.info(e)


@app.task
def common_callback(url, params, channel):
    callback(url, params, channel)


@app.task
def common_callback_for_post(url, params, channel):
    logger.info("Enter %s_callback task===>>>" % channel)
    ret = None
    try:
        logger.info(params)
        ret = requests.post(url, data=params)
        logger.info('%s callback url: %s' % (channel, ret.url))
        logger.info('callback return: %s' % ret.text)
    except Exception, e:
        logger.info(" {'%s callback':'failed to connect'} " % channel)
        logger.info(e)

    if ret:
        logger.info(ret.text)


@app.task
def bajinshe_account_push(user_id):
    logger.info("enter bajinshe_account_push with user[%s]" % user_id)
    push_url = settings.BAJINSHE_ACCOUNT_PUSH_URL
    coop_id = settings.BAJINSHE_COOP_ID
    coop_key = settings.BAJINSHE_COOP_KEY
    order_id = '%s_0001' % timezone.now().strftime("%Y%m%d%H%M%S")
    access_token, message = get_bajinshe_access_token(coop_id, coop_key, order_id)
    if access_token:
        bid = get_tid_for_coop(user_id)
        if bid:
            phone = get_user_phone_for_coop(user_id)
            account_data = [{
                'bingdingUid': bid,
                'usn': phone,
                'sumIncome': 0,
                'totalBalance': 0,
                'availableBalance': 0,
            }]

            data = {
                'access_token': access_token,
                'platform': coop_id,
                'order_id': order_id,
                'tran': account_data,
            }

            headers = {
               'Content-Type': 'application/json',
            }
            data = json.dumps(data)
            res = requests.post(url=push_url, data=data, headers=headers)
            res_status_code = res.status_code
            logger.info("bajinshe account push url %s" % res.url)
            if res_status_code == 200:
                res_data = res.json()
                if res_data['code'] != '10000':
                    logger.info("bajinshe push account return %s" % res_data)
                else:
                    logger.info("bajinshe push account data[%s] suceess" % data)
            else:
                logger.info("bajinshe push account connect failed with status code [%s]" % res_status_code)
                logger.info(res.text)


@app.task
def bajinshe_recharge_push(user_id, order_id):
    push_url = settings.BAJINSHE_RECHARGE_PUSH_URL
    coop_id = settings.BAJINSHE_COOP_ID
    coop_key = settings.BAJINSHE_COOP_KEY
    order_id = '%s_0002' % timezone.now().strftime("%Y%m%d%H%M%S")
    access_token, message = get_bajinshe_access_token(coop_id, coop_key, order_id)
    if access_token:
        bid = get_tid_for_coop(user_id)
        penny = Decimal(0.01).quantize(Decimal('.01'))
        pay_info = PayInfo.objects.filter(user=user_id, type='D', amount__gt=penny,
                                          status=PayInfo.SUCCESS, order=order_id).first()
        if bid and pay_info:
            phone = get_user_phone_for_coop(user_id)
            account_data = [{
                'bingdingUid': bid,
                'usn': phone,
                'businessName': '',
                'businessType': '',
                'businessBid': '',
                'money': pay_info.amount,
                'sumIncome': 0,
                'totalBalance': 0,
                'availableBalance': 0,
            }]

            data = {
                'access_token': access_token,
                'platform': coop_id,
                'order_id': order_id,
                'tran': account_data,
            }

            headers = {
               'Content-Type': 'application/json',
            }
            data = json.dumps(data)
            res = requests.post(url=push_url, data=data, headers=headers)
            res_status_code = res.status_code
            logger.info("bajinshe account push url %s" % res.url)
            if res_status_code == 200:
                res_data = res.json()
                if res_data['code'] != '10000':
                    logger.info("bajinshe push account return %s" % res_data)
                else:
                    logger.info("bajinshe push account data[%s] suceess" % data)
            else:
                logger.info("bajinshe push account connect failed with status code [%s]" % res_status_code)
                logger.info(res.text)


@app.task
def bajinshe_transaction_push(user_id, order_id):
    push_url = settings.BAJINSHE_RECHARGE_PUSH_URL
    coop_id = settings.BAJINSHE_COOP_ID
    coop_key = settings.BAJINSHE_COOP_KEY
    access_token, message = get_bajinshe_access_token(coop_id, coop_key, order_id)
    if access_token:
        bid = get_tid_for_coop(user_id)
        margin_record = MarginRecord.object(user_id=user_id, order_id=order_id).first()
        if bid and margin_record:
            phone = get_user_phone_for_coop(user_id)
            account_data = [{
                'bingdingUid': bid,
                'usn': phone,
                'businessName': '',
                'businessType': margin_record.catalog,
                'businessBid': order_id,
                'money': margin_record.amount,
                'time': timezone.localtime(margin_record.create_time()).strftime('%Y%m%d%H%M%S'),
                'moneyType': '',
                'availableBalance': margin_record.margin_current,
            }]

            data = {
                'access_token': access_token,
                'platform': coop_id,
                'order_id': order_id,
                'tran': account_data,
            }

            headers = {
               'Content-Type': 'application/json',
            }
            data = json.dumps(data)
            res = requests.post(url=push_url, data=data, headers=headers)
            res_status_code = res.status_code
            logger.info("bajinshe account push url %s" % res.url)
            if res_status_code == 200:
                res_data = res.json()
                if res_data['code'] != '10000':
                    logger.info("bajinshe push account return %s" % res_data)
                else:
                    logger.info("bajinshe push account data[%s] suceess" % data)
            else:
                logger.info("bajinshe push account connect failed with status code [%s]" % res_status_code)
                logger.info(res.text)
