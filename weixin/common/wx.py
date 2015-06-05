# encoding:utf-8
from __future__ import unicode_literals
from django.conf import settings
from weixin.models import WeixinAccounts
from weixin.common.wxpay import JSWXpay
from django.core.urlresolvers import reverse


def get_host_url(request):
    host_url = '{}{}'.format(['http://', 'https://'][settings.ENV != settings.ENV_DEV], request.get_host())
    return host_url


def generate_js_wxpay(request):
    account_main = WeixinAccounts.get('main')
    js_wxpay = JSWXpay(
        appid=account_main.app_id,
        mch_id=account_main.mch_id,
        key=account_main.key,
        ip='119.254.110.30',
        notify_url='{}{}'.format(get_host_url(request), reverse('weixin_pay_notify')),
        appsecret=account_main.app_secret
    )
    return js_wxpay