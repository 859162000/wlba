# coding=UTF-8
from dateutil.relativedelta import relativedelta

from django import template
from django.utils import timezone
from django.conf import settings

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
    return _money_format(value)

@register.filter
def money_format_int(value):
    value = "%.0f" % value
    return _money_format(value)


def _money_format(value):
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
    rs = "%s" % value
    return "%s%%" % rs[:rs.find(".")+2]
    #return u'%.1f%%' % (value, )

@register.filter
def percentage_number(value):
    return u'%.1f' % (value, )

@register.filter
def percentage_number_two(value):
    return u'%.1f' % (value*100, )

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


def safe_phone_str(phone):
    return phone[:3] + '*' * (len(phone) - 2 - 3) + phone[-2:]


@register.filter
def safe_phone_new(phone):
    return phone[:3] + '*' * (len(phone) - 2 - 3) + phone[-2:]


@register.filter
def safe_phone(user):
    """
    Show part of user identifier, used in password reset page
    """

    result = u''
    if user.wanglibaouserprofile.phone:
        result = safe_phone_str(user.wanglibaouserprofile.phone)

    return result

@register.filter
def safe_id(id_number):
    """
    Show part of id_number
    """

    result = id_number[:-12] + '*' * 12

    return result

@register.filter
def safe_name(name):
    """
    Show part of name
    """

    result = "*" + name[1:]
    return result

@register.filter
def safe_name_last(name):
    """
    Show part of name
    """

    result = name[:1] + "*" * 3
    return result

@register.filter
def safe_name_first(name):
    """
    Show last word
    """

    result = "*" * 2 + name[-1]
    return result

@register.filter
def safe_address(name):
    """
    Show part of name
    """

    result = name[:3] + '*' * 3
    return result

@register.filter
def display_name(user):
    if user.wanglibaouserprofile.nick_name:
        return user.wanglibaouserprofile.nick_name

    return safe_phone(user)

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
    if time_delta.days >= 0:
        hours, seconds = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        hours += time_delta.days * 24
        return "%d:%02d:%02d" % (hours, minutes, seconds)
    else:
        return "00:00:00"

@register.filter
def timedelta_now_day(time):
    time_delta = time - timezone.now()
    days = time_delta.days
    if days >= 0:
        hours, seconds = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        if days > 0:
            return "%d天%d小时%02d分%02d秒" % (days, hours, minutes, seconds)
        else:
            return "%d小时%02d分%02d秒" % (hours, minutes, seconds)
    else:
        return ""

@register.filter
def milltime_format(time):
    from datetime import datetime
    format_time = datetime.fromtimestamp(time)
    return format_time.strftime('%Y-%m-%d %H:%M:%S')

@register.filter
def milldate_format(time):
    from datetime import datetime
    format_time = datetime.fromtimestamp(time)
    return format_time.strftime('%Y-%m-%d')


@register.filter
def card_info(card):
    return u"%s(尾号%s)" % (card.bank.name, card.no[-4:])

@register.filter
def last_four_char(str):
    if str:
        return str[-4:]
    else:
        return ""


@register.filter
def number_to_chinese(value):
    nums = "%.2f" % value

    left, right = nums.split('.')

    number_charactors = list(u'零壹贰叁肆伍陆柒捌玖')
    unit_charactors = list(u'万仟佰拾 仟佰拾 仟佰拾 ')[-len(left):]
    units = list(u'                   亿   万   元')[-len(left):]

    nums = [int(d) for d in left]

    result = u''

    zero = False

    for i in range(0, len(nums)):
        if zero and nums[i] != 0:
            result += number_charactors[0]

        if nums[i] != 0:
            result += number_charactors[nums[i]]
            if unit_charactors[i] != ' ':
                result += unit_charactors[i]

        if units[i] != ' ':
            result += units[i]

        if nums[i] == 0:
            zero = True
        else:
            zero = False

    result = result.replace(u'亿万', u'亿')

    if right == '00':
        result += u'整'
    else:
        jiao, fen = [int(d) for d in right]

        if jiao:
            result += number_charactors[jiao] + u'角'
        if fen:
            result += number_charactors[fen] + u'分'

    return result


@register.filter
def add_months(value, months):
    return value + relativedelta(months=months)

@register.filter
def safe_paytype(value):
    if value == 'W':
        return u'取款'
    else:
        return u'充值'

@register.filter
def admin_address(value):
    """
    Convert the number into 10k based string
    """
    return settings.ADMIN_ADDRESS


@register.filter
def period_unit(value):
    import re
    matches = re.search(u'日计息', value)
    if matches and matches.group():
        return u'天'
    else:
        return u'个月'
