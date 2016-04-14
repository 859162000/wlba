#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
from wanglibao.celery import app

logger = logging.getLogger('wanglibao_tasks')


@app.task
def common_callback(channel, url, params, req_action=1, headers=None):
    logger.info("Enter %s_callback task===>>>" % channel)

    try:
        logger.info(params)

        if req_action == 1:
            if headers:
                ret = requests.post(url, data=params, headers=headers)
            else:
                ret = requests.post(url, data=params)
        else:
            ret = requests.get(url, params=params)

        logger.info('%s callback url: %s' % (channel, ret.url))
        logger.info('callback return: %s' % ret.text)
    except Exception, e:
        logger.info(" {'%s callback':'failed to connect'} " % channel)
        logger.info(e)
        ret = None

    return ret
