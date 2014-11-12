# coding=utf-8
from datetime import timedelta
from django.utils import timezone

def format_datetime(time, fmt):
    return timezone.localtime(time).strftime(fmt.encode('utf-8')).decode('utf-8')


def suffix(f):
    def wrapper(*args, **kwargs):
        return unicode(f(*args, **kwargs)) + u'回复TD退订 400-858-8066【网利宝】'
    return wrapper

@suffix
def deposit_succeed(amount):
    return u'充值操作成功，充值金额%s元。' % str(amount)

@suffix
def withdraw_failed(error_message):
    if len(error_message) < 1:
        return u'提现失败，请到网站查看余额，联系客服人员再次提现。'
    return u'提现失败，原因如下：%s' % error_message

@suffix
def withdraw_submitted(amount, issue_time):
    #arrive_date = issue_time + timedelta(days=3)
    #return u'提现申请成功，申请金额%s元，预计%s前到账。' % (str(amount), format_datetime(arrive_date, u'%Y年%m月%d日'))
    return u'提现申请成功，申请金额%s元，预计3个工作日内到账。' % amount

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
    return u'您的验证码%s' % code


@suffix
def gift_inviter(invited_phone, money):
    return u'用户%s已接受你的邀请注册网利宝并购买成功！网利宝将奖励你%s元手机话费，5个工作日内将直接充值到你的注册手机号。' \
           % (invited_phone, str(money))

@suffix
def gift_invited(inviter_phone, money):
    return u'感谢你接受用户%s的邀请注册网利宝并成功购买理财产品！网利宝将奖励你%s元手机话费，5个工作日内将直接充值到你的注册手机号。' \
           % (inviter_phone, str(money))

@suffix
def rand_pass(password):
    return u'感谢注册网利宝，您的初始密码是%s，请登录wanglibao.com修改密码。' % password

@suffix
def earning_message(amount):
    return u'亲，您的投标奖励收益%s元，已赠送到您的网利宝账户，可用于理财投资' % amount

@suffix
def reg_reward_message(xunlei_code):
    return u'感谢注册成功。迅雷白金会员激活码%s有效期2015年12月31日回复TD退订4008-588-066' % xunlei_code

@suffix
def purchase_reward_message(xunlei_code):
    return u'恭喜理财成功。迅雷白金会员激活码%s有效期2015年12月31日回复TD退订4008-588-066' % xunlei_code

#站内信模板
def msg_bid_purchase(order_id, product_name, amount):
    title = u"投标通知"
    content = u"感谢您投资订单号【%s】借款项目“%s”￥%s元，该项目正在招标中，您的投标资金暂时被冻结，满标后将放款计息。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % (order_id, product_name, amount)
    return title, content

def msg_bid_fail(product_name):
    title = u"流标通知"
    content = u"感谢您投资 借款项目“%s”，该项目在有效期内未满标，视为流标，您的该笔投资金额已取消冻结，您可继续投资其他理财产品。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % product_name
    return title, content

def msg_register_authok(activation):
    title = u"注册成功"
    content = u"感谢您注册网利宝。<br/>网利宝赠送您3天迅雷白金会员激活码，请您查收！<br/>激活码：%s，有效期至2015年12月31日。<br/>立即兑换（<a href='http://pay.vip.xunlei.com/baijin.html' target='_blank'>http://pay.vip.xunlei.com/baijin.html</a>）<br/>感谢您对我们的支持与关注。<br/>网利宝" % activation
    return title, content

def msg_first_licai(activation):
    title = u"活动期首次理财成功"
    content = u"感谢您在活动期间完成首次理财。<br/>网利宝赠送您1个月迅雷白金会员激活码，请您查收！<br/>激活码：%s，有效期至2015年12月31日。<br/>立即兑换（<a href='http://pay.vip.xunlei.com/baijin.html' target='_blank'>http://pay.vip.xunlei.com/baijin.html</a>）<br/>感谢您对我们的支持与关注。<br/>网利宝" % activation
    return title, content

def msg_invite_major(inviter, invited):
    title = u"邀请好友送话费"
    content = u"您的好友%s已通过您的邀请完成网利宝投资，您和您好友将共享60元话费,您的30元话费将于3个工作日内充值至您的手机号%s，请注意查收。<br/>感谢您对我们的支持与关注！<br/>网利宝" % (invited, inviter)
    return title, content

def msg_invite_are(inviter, invited):
    title = u"邀请好友送话费"
    content = u"您已和您的好友%s成功建立邀请关系，您和您好友将共享60元话费,您的30元话费将于3个工作日内充值至您的手机号%s，请注意查收。<br/>感谢您对我们的支持与关注！<br/>网利宝" % (inviter, invited)
    return title, content

def msg_bid_success(product_name, date):
    title = u"投标成功通知"
    content = u"感谢您投资 借款项目“%s”，该项目已满标放款，将于%s开始计息。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % (product_name, date)
    return title, content

def msg_withdraw(withtime, amount):
    title = u"申请提现"
    content = u"您于%s申请的提现￥%s元已经提交，如您填写的账户信息正确无误，您的资金将会于3个工作日内到达您的银行账户。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % (format_datetime(withtime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content

def msg_withdraw_fail(withtime, amount):
    title=u"提现结果"
    content = u"您于%s申请的提现￥%s元，由于您填写的银行账户信息有误，未能成功汇款。请您填写正确的银行账户信息，重新提交申请。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % (format_datetime(withtime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content

def msg_withdraw_success(withtime, amount):
    title = u"提现成功"
    content = u"您于%s申请的提现￥%s元，已汇款，请注意查收。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % (format_datetime(withtime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content

def msg_bid_repay(product_name, retime, amount):
    title = u"项目还款"
    content = u"借款项目“%s”第1/3期于%s还款￥%s元，请注意查收。<br/>查看账户余额（超链）<br/>感谢您对我们的支持与关注。<br/>网利宝" % (product_name, format_datetime(retime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content

