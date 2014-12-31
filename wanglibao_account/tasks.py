#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rsj217'

from wanglibao_p2p.models import P2PProduct
from wanglibao_account.utils import CjdaoUtils
from wanglibao.settings import CJDAOKEY, POST_PRODUCT_URL
from wanglibao.celery import app
import requests
import logging


logger = logging.getLogger('p2p')


@app.task
def cjdao_callback(url, params):
    r = requests.get(url, params=params)

    print('#' * 80)
    print(r.url)
    print(r.status_code)
    print(r.text)

    logger.debug(params)
    logger.debug('#' * 80)
    logger.debug(r.url)
    logger.debug(r.status_code)
    logger.debug(r.text)


@app.task
def post_product_half_hour():
    p2p = P2PProduct.objects.filter(hide=False).filter(status__in=[u'正在招标', u'满标待打款', u'满标已打款', u'满标待审核'])
    p = CjdaoUtils.post_product(p2p, CJDAOKEY)

    r = requests.get(POST_PRODUCT_URL, params=p)

    print('#' * 80)
    print(r.url)
    print(r.status_code)
    print(r.text)

    logger.debug(r)
    logger.debug('#' * 80)
    logger.debug(r.url)
    logger.debug(r.status_code)
    logger.debug(r.text)
