# encoding:utf-8
from __future__ import unicode_literals
import requests
from django.core.cache import cache


def get_access_token(app_id, app_secret, expires_in=7000):
    key = 'access_token_%s_%s' % (app_id, app_secret)
    if cache.get(key):
        return cache.get(key)

    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
    res = requests.get(url % (app_id, app_secret)).json()
    cache.set(key, res, expires_in)
    return res


def get_jsapi_ticket(access_token, expires_in=7000):
    key = 'jsapi_ticket_%s' % access_token
    if cache.get(key):
        return cache.get(key)

    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi'
    res = requests.get(url % access_token).json()
    cache.set(key, res, expires_in)
    return res