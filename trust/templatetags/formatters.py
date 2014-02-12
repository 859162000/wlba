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
