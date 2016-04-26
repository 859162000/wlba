#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import StringIO
import traceback
from wanglibao.celery import app
from .models import CallbackRecord

logger = logging.getLogger('wanglibao_tasks')

LOCAL_VAR = locals()


def bajinshe_callback_ret_parser(ret, channel, order_id=None):
    ret_data = ret.json()
    if order_id:
        call_back_record = CallbackRecord.objects.filter(callback_to=channel, order_id=order_id).first()
        if call_back_record:
            call_back_record.result_code = ret_data.get('code')
            call_back_record.result_msg = ret_data.get('msg')
            call_back_record.result_errors = ret_data.get('errors')
            call_back_record.save()


def renrenli_callback_ret_parser(ret, channel, order_id=None):
    ret_data = ret.json()
    if order_id:
        call_back_record = CallbackRecord.objects.filter(callback_to=channel, order_id=order_id).first()
        if call_back_record:
            call_back_record.result_code = ret_data.get('Code')
            call_back_record.result_msg = ret_data.get('Tip')
            call_back_record.save()


def bisouyi_callback_ret_parser(ret, channel, order_id=None):
    ret_data = ret.json()
    if order_id:
        call_back_record = CallbackRecord.objects.filter(callback_to=channel, order_id=order_id).first()
        if call_back_record:
            call_back_record.result_code = ret_data.get('code')
            call_back_record.result_msg = ret_data.get('message')
            call_back_record.save()


@app.task
def common_callback(channel, url, params, req_action='POST', headers=None, order_id=None, ret_parser=''):
    logger.info("Enter %s_callback task===>>>" % channel)

    try:
        logger.info("callback_order_id[%s] with params[%s]" % (order_id, params))

        if req_action == 'POST':
            if headers:
                ret = requests.post(url, data=params, headers=headers)
            else:
                ret = requests.post(url, data=params)
        else:
            ret = requests.get(url, params=params)

        logger.info('%s callback url: %s' % (channel, ret.url))
        logger.info('callback return: %s' % ret.text)

        if ret and ret.status_code == 200 and ret_parser:
            ret_parser = LOCAL_VAR[ret_parser]
            ret_parser(ret, channel, order_id)
    except:
        # 创建内存文件对象
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        logger.info(" {'%s callback':'failed to connect'} " % channel)
        logger.info(message)
        ret = None

    return ret
