#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rsj217'


from utils import CjdaoUtils
import requests


def gendata():

    k = ('thirdproductid', 'productname', 'companyname', 'startinvestmentmoney', 'acceptinvestmentmoney',
    'loandeadline','expectedrate', 'risktype', 'incomeway', 'creditrating', 'iscurrent', 'isredeem', 'isassignment')

    v = ('721', '测试发标', '网利宝', '100', '100000', '3',
        '0.13', '1', '1', 'a', '1', '1', '1', '1234')

    p = dict(zip(k, v))
    p.update(md5_value=CjdaoUtils.md5_value(*v))
    url = 'http://test.cjdao.com/p2p/saveproduct'
    return url, p



