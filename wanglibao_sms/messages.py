# coding=utf-8
from django.utils import timezone

suffix = u'回复TD退订 400-858-8066【网利宝】'


def send_validate_code(phone, code):
    return u'手机尾号[%s]的验证码是[%s]，欢迎使用网利宝，您的贴心理财专家！%s' % phone[-4:], code, suffix


def reset_password(code):
    return u'[%s]（找回密码验证码）%s' % code, suffix


def send_password(phone, password):
    return u'手机尾号[%s]的密码是[%s]，欢迎使用网利宝，您的贴心理财专家！%s' % phone[-4:], password, suffix


def login_notification():
    return u'您的账号在其它设备登录，如非您本人操作，请及时更改密码。若更换了手机号码，请联系客服解绑。'


def order_notification(order_date, product_name, end_date):
    return u'您在%s申购的%s将于%s到期，您可继续持有，或在到期后取现购买其它理财产品。%s' % order_date, product_name, end_date, suffix


def product_redeemed_today(order_date, product_name):
    return u'您在%s申购的%s已于今日（%s）到期，您可继续持有，或在到期后取现购买其它理财产品。%s' % order_date, \
           product_name, \
           timezone.now().strftime('%Y-%m-%d'), \
           suffix


def bought_notification(product_name):
    return u'%s已经购买成功，9点显示收益。%s' % product_name, suffix


def processing_purchase():
    return u'购买处理中，正在进行确认，成功后将于9点显示收益。%s' % suffix

