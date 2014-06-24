# coding=UTF-8

from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def money_to_10k(value):
    """
    Convert the number into 10k based string
    """
    return u'%d万' % (int(value),)

@register.filter
def convert_to_10k(value):
    """
    Convert the number into 10k or 10000k based string
    """
    value = int(float(value))
    return u'%s 万' % (value/10000)

@register.filter
def money(value):
    """
    Convert the number into 10k based string
    """
    return u'%d元' % (int(value),)

@register.filter
def money_f_2(value):
    """
    Convert the number into xx.xx
    """
    return u'%.2f' % value

@register.filter
def money_format(value):
    value = "%.2f" % value
    components = str(value).split('.')
    if len(components) > 1:
        left, right = components
        right = '.' + right
    else:
        left, right = components[0], ''

    result = ''
    while left:
        result = left[-3:] + ',' + result
        left = left[:-3]
    return result.strip(',') + right

@register.filter
def month(value):
    """
    Convert the float based month to string
    """
    return u'%d个月' % (int(value), )

@register.filter
def day(value):
    """
    Convert the float based month to string
    """
    return u'%d天' % (int(value), )

@register.filter
def percentage(value):
    """
    Convert float based percentage to string
    """
    return u'%.1f%%' % (value, )

@register.filter
def yes_no(value):
    if value:
        return u'是'
    else:
        return u'否'

@register.filter
def na_if_none(value):
    if value is None or value == '':
        return u'--'
    else:
        return value

@register.filter
def safe_mail(user):
    """
    Show part of user identifier, used in password reset page
    """

    result = u''
    if user.email:
        components = user.email.split('@')
        name = components[0]
        name = name[0] + '*' * (len(name)-2) + name[-1]
        result = name + '@' + components[1]

    return result

@register.filter
def safe_phone(user):
    """
    Show part of user identifier, used in password reset page
    """

    result = u''
    if user.wanglibaouserprofile.phone:
        phone = user.wanglibaouserprofile.phone
        result = phone[:3] + '*' * (len(phone) - 4 - 3) + phone[-4:]

    return result

@register.filter
def safe_id(id_number):
    """
    Show part of id_number
    """

    result = id_number[:6] + '*' * 8 + id_number[13:]
    return result

@register.filter
def safe_name(name):
    """
    Show part of name
    """

    result = "*" + name[1:]
    return result


@register.filter
def not_bool_to_display(flag):
    if flag:
        return 'display: none'
    return ''

mapping = {
  'gmail.com': 'https://mail.google.com/',
  '163.com': 'http://mail.163.com/',
  '126.com': 'http://mail.126.com/',
  'qq.com': 'http://mail.qq.com/',
  'sina.com': 'http://mail.sina.com/',
  'sohu.com': 'http://mail.sohu.com/',
  'yahoo.com.cn': 'http://mail.yahoo.com.cn/',
  'yahoo.com': 'http://mail.yahoo.com/',
  'yahoo.cn': 'http://mail.cn.yahoo.com/',
  '21.cn': 'http://mail.21cn.com/',
  '139.com': 'http://mail.139.com/',
  '263.net': 'http://mail.263.net/',
  'hotmail.com': 'http://www.hotmail.com/',
  'msn.com': 'http://www.hotmail.com/',
}

@register.filter
def mail_login_url(email):
    if not email:
        return ''
    domain = email.strip().split('@')[1]
    if domain in mapping:
        return mapping[domain]
    return 'http://www.baidu.com/#wd=%' % domain

@register.filter
def current_deposit_times(profit):
    times = profit / 0.35
    return '%.1f' % times

@register.filter()
def bank_card(no):
    return no[:4] + ' **** **** ' + no[-4:]

@register.filter()
def get_range(start, end):
    return range(start, end)

@register.filter()
def buy_fund_url(code):
    return '/shumi/oauth/check_oauth_status/?fund_code='+ code + '&action=purchase'

@register.filter
def timedelta_now(time):
    time_delta = time - timezone.now()
    hours, seconds = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    hours += time_delta.days * 24
    return "%d:%02d:%02d" % (hours, minutes, seconds)