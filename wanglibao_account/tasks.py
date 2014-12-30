#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rsj217'


from wanglibao.celery import app
import requests
import logging


logger = logging.getLogger('p2p')

@app.task
def cjdao_callback(url, params):
    r = requests.get(url, params=params)


    logger.debug(params)
    logger.debug('#'*80)
    logger.debug(r.url)
    logger.debug(r.status_code)
    logger.debug(r.text)
