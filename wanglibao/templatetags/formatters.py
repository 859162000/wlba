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
def percentage(value):
    """
    Convert float based percentage to string
    """
    return u'%.2f%%' % (value, )

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