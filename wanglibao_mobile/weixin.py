# encoding:utf-8
from __future__ import unicode_literals
from django.core.cache import cache
from collections import OrderedDict
import uuid
import time
import hashlib
import requests


class OfficialAPIError(Exception):
    """
    微信官方API请求出错异常
    """
    pass


def request_api(method, url):
    """
    请求微信官方API
    :param method:
    :param url:
    :return:
    """
    res = requests.request(method, url).json()
    if not res:
        raise OfficialAPIError('微信官方API请求出错异常')
    elif res.get('errcode'):
        raise OfficialAPIError(res)
    return res


def request_api_use_cache(method, url, key, expires_in):
    """
    请求微信官方API  结果使用缓存
    :param method:
    :param url:
    :param key:
    :param expires_in:
    :return:
    """
    if cache.get(key):
        return cache.get(key)
    res = request_api(method, url)
    cache.set(key, res, expires_in)
    return res


def get_access_token(app_id, app_secret, expires_in=7200 - 60):
    """
    获取公众号的 access token
    :param app_id:
    :param app_secret:
    :param expires_in:
    :return:
    """
    key = 'access_token_%s_%s' % (app_id, app_secret)
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
    url = url % (app_id, app_secret)
    return request_api_use_cache('GET', url, key, expires_in)


def get_jsapi_ticket(access_token, expires_in=7200 - 60):
    """
    获取 js api ticket
    :param access_token:
    :param expires_in:
    :return:
    """
    key = 'jsapi_ticket_%s' % access_token
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi'
    url = url % access_token
    return request_api_use_cache('GET', url, key, expires_in)


def generate_weixin_jssdk_config(app_id, app_secret, url):
    """
    生成微信JS-SDK的配置信息
    :param app_id:
    :param app_secret:
    :param url: 使用微信JS-SDK的页面地址
    :return:
    """
    access_token = get_access_token(app_id, app_secret).get('access_token')
    jsapi_ticket = get_jsapi_ticket(access_token).get('ticket')

    params = OrderedDict()
    params['jsapi_ticket'] = jsapi_ticket
    params['noncestr'] = uuid.uuid1().hex
    params['timestamp'] = str(int(time.time()))
    params['url'] = url.split('#')[0]
    string = '&'.join(['%s=%s' % (k, v) for k, v in params.items()])
    signature = hashlib.sha1(string).hexdigest()

    data = {
        'noncestr': params.get('noncestr'),
        'timestamp': params.get('timestamp'),
        'signature': signature,
    }

    return data