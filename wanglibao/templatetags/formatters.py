# coding=UTF-8

from django import template

register = template.Library()

@register.filter
def money_to_10k(value):
    """
    Convert the number into 10k based string
    """
    return u'%d万' % (int(value),)

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
