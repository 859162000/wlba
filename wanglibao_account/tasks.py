#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import urllib
from wanglibao.celery import app

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
