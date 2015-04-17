# encoding:utf-8
from __future__ import unicode_literals
import requests
from django.core.cache import cache


class OfficialAPIError(Exception):
    """
    微信官方API请求出错异常
    """
    pass


def request_api(method, url):
    res = requests.request(method, url).json()
    if not res:
        raise OfficialAPIError('微信官方API请求出错异常')
    elif res.get('errcode'):
        raise OfficialAPIError(res)
    return res


def request_api_use_cache(method, url, key, expires_in):
    if cache.get(key):
        return cache.get(key)
    res = request_api(method, url)
    cache.set(key, res, expires_in)
    return res


def get_access_token(app_id, app_secret, expires_in=7000):
    key = 'access_token_%s_%s' % (app_id, app_secret)
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
    url = url % (app_id, app_secret)
    return request_api_use_cache('GET', url, key, expires_in)


def get_jsapi_ticket(access_token, expires_in=7000):
    key = 'jsapi_ticket_%s' % access_token
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi'
    url = url % access_token
    return request_api_use_cache('GET', url, key, expires_in)