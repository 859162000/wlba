#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wanglibao_account.cooperation import xicai_send_data

__author__ = 'rsj217'
import requests
import urllib
import logging
from wanglibao.celery import app

from wanglibao_account.models import Binding

# from wanglibao_p2p.models import P2PProduct
# from wanglibao_account.utils import CjdaoUtils
# from wanglibao.settings import CJDAOKEY, POST_PRODUCT_URL
# from wanglibao.celery import app
# import requests
# import logging
#
#
logger = logging.getLogger(__name__)
#
#
# @app.task
# def cjdao_callback(url, params):
#     r = requests.get(url, params=params)
#
#     print('#' * 80)
#     print(r.url)
#     print(r.status_code)
#     print(r.text)
#
#     logger.debug(params)
#     logger.debug('#' * 80)
#     logger.debug(r.url)
#     logger.debug(r.status_code)
#     logger.debug(r.text)
#
#
# @app.task
# def post_product_half_hour():
#     p2ps = P2PProduct.objects.filter(hide=False).filter(status__in=[u'正在招标', u'满标待打款', u'满标待审核'])
#
#
#     logger.debug('p2p的产品数目 %s' % p2ps.count())
#
#     for p2p in p2ps:
#         p = CjdaoUtils.post_product(p2p, CJDAOKEY)
#         r = requests.get(POST_PRODUCT_URL, params=p)
#
#         print('#' * 80)
#         print(r.url)
#         print(r.status_code)
#         print(r.text)
#
#         logger.debug(r)
#         logger.debug('#' * 80)
#         logger.debug(r.url)
#         logger.debug(r.status_code)
#         logger.debug(r.text)
#         logger.debug(p2p.id)


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
def yiruite_callback(url, params):
    ret = callback(url, params, 'yiruite')
    if ret.text == 'success':
        logger.info(" {'msg':'success'} ")
    elif ret.text == 'error_tid':
        logger.info(" {'errorcode':'error_tid', 'errormsg':'交易号错误'} ")
    elif ret.text == 'error_1':
        logger.info(" {'errorcode':'error_1', 'errormsg':'交易号重复处理过'} ")
    elif ret.text == 'error_2':
        logger.info(" {'errorcode':'error_2', 'errormsg':'Ip完成过'} ")
    elif ret.text == 'error_3':
        logger.info(" {'errorcode':'error_3', 'errormsg':'一天内ip段完成过'} ")
    elif ret.text == 'error_safe_filename:':
        logger.info(" {'errorcode':'error_safe_filename', 'errormsg':'回调文件与交易号不匹配'} ")
    elif ret.text == 'error_callback_ip:':
        logger.info(" {'errorcode':'error_callback_ip', 'errormsg':'广告方IP加调不正确'} ")
    elif ret.text == 'error_sign:':
        logger.info(" {'errorcode':'error_sign', 'errormsg':'签名不正确'} ")
    else:
        pass

@app.task
def xicai_send_data_task():
    """
    向希财网更新数据
    :return:
    """
    xicai_send_data()














