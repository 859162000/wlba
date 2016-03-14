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
from .utils import get_bajinshe_access_token, get_bajinshe_base_data
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
def bajinshe_callback(url, data):
    logger.info("enter bajinshe callback with url[%s] data[%s]" % (url, data))
    headers = {
       'Content-Type': 'application/json',
    }
    try:
        res = requests.post(url=url, data=data, headers=headers)
    except Exception, e:
        logger.info("bajinshe callback connect failed with error: %s" % e)
    else:
        res_status_code = res.status_code
        if res_status_code == 200:
            logger.info(">>>>>>>>>>>>>>>%s" % data)
            logger.info("bajinshe callback return %s" % res.json())
        else:
            logger.info("bajinshe callback connect failed with status code [%s]" % res_status_code)
            logger.info(res.text)


@app.task
def renrenli_callback(url, data):
    logger.info("enter renrenli callback with url[%s]" % url)
    headers = {
       'Content-Type': 'application/json',
    }
    data = json.dumps(data)
    try:
        res = requests.post(url=url, data=data, headers=headers)
    except Exception, e:
        logger.info("renrenli callback connect failed with error: %s" % e)
    else:
        res_status_code = res.status_code
        if res_status_code == 200:
            res_data = res.json()
            if res_data['Code'] != '101':
                logger.info("renrenli callback return %s" % res_data)
            else:
                logger.info("renrenli callback data[%s] suceess" % data)
        else:
            logger.info("renrenli callback connect failed with status code [%s]" % res_status_code)
            logger.info(res.text)
