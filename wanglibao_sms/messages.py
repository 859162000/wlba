# coding=utf-8
from datetime import timedelta


def format_datetime(time, fmt):
    return time.strftime(fmt.encode('utf-8')).decode('utf-8')


def suffix(f):
    def wrapper(*args, **kwargs):
        return unicode(f(*args, **kwargs)) + u'回复TD退订 400-858-8066【网利宝】'
    return wrapper

@suffix
def deposit_succeed(amount):
    return u'充值操作成功，充值金额%s元。' % str(amount)

@suffix
def withdraw_submitted(amount, issue_time):
    arrive_date = issue_time + timedelta(days=3)
    return u'提现申请成功，申请金额%s元，预计%s前到账。' % (str(amount), format_datetime(arrive_date, u'%Y年%m月%d日'))

@suffix
def product_settled(product, settled_time):
    return u'%s[%s]已投资成功，并于%s开始计息。' % (product.short_name,
                                            product.serial_number,
                                            format_datetime(settled_time, u'%Y年%m月%d日'))

@suffix
def product_failed(product):
    return u'%s[%s]在%s之前未满标，投标失败。投标账款已退回网利宝平台账户中。' % (product.short_name,
                                                      product.serial_number,
                                                      format_datetime(product.end_time, u'%Y年%m月%d日%H:%M'))

@suffix
def product_amortize(product, amortize_time, amount):
    return u'%s[%s]，于%s收到还款%s元。' % (product.short_name,
                                    product.serial_number,
                                    format_datetime(amortize_time, u'%Y年%m月%d日%H:%M'),
                                    str(amount))

@suffix
def validate_code(code):
    return u'验证码%s，如非本人操作，请忽略。工作人员不会索取，请勿泄露。' % code


@suffix
def gift_inviter(invited_phone, money):
    return u'用户%s已接受你的邀请注册网利宝并购买成功！网利宝将奖励你%s元手机话费，5个工作日内将直接充值到你的注册手机号。' \
           % (invited_phone, str(money))

@suffix
def gift_invited(inviter_phone, money):
    return u'感谢你接受用户%s的邀请注册网利宝并成功购买理财产品！网利宝将奖励你%s元手机话费，5个工作日内将直接充值到你的注册手机号。' \
           % (inviter_phone, str(money))
