# coding=utf-8
from datetime import timedelta
from django.utils import timezone


def format_datetime(time, fmt):
    return timezone.localtime(time).strftime(fmt.encode('utf-8')).decode('utf-8')


def suffix(f):
    def wrapper(*args, **kwargs):
        return unicode(f(*args, **kwargs)) + u'【网利科技】'
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
    return u'您投资的%s项目收到还款%s元，已到帐。' % (product.short_name, str(amount))


@suffix
def product_prepayment(product, amortize_time, amount):
    return u'您投资的%s项目已提前还款%s元，已到帐。' % (product.short_name, str(amount))

@suffix
def validate_code(code):
    return u'您的验证码%s' % code


@suffix
def rand_pass(password):
    return u'感谢注册网利宝，您的初始密码是%s，请登录wanglibao.com修改密码。' % password


@suffix
def earning_message(amount):
    return u'亲，您的投标奖励%s%s收益，已赠送到您的网利宝账户，可用于理财投资。详情请登陆网利宝查看站内信。' % (amount, u'%')


@suffix
def product_full_message(name):
    return u'%s，满标了。' % name


#站内信模板
def msg_bid_purchase(order_id, product_name, amount):
    title = u"投标通知"
    content = u"感谢您投资订单号【%s】借款项目“%s”￥%s元，该项目正在招标中，您的投标资金暂时被冻结，满标后将放款计息。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % (order_id, product_name, amount)
    return title, content


def msg_bid_earning(product_name, activity_name, term, time, earning_percent, earning_aoumnt, unit):
    title = u"活动收益"
    content = u"借款项目“%s(%s）,期限%s%s”于%s赠送【%s%s】活动收益【%s】元，请注意查收。 查看账户余额 感谢您对我们的支持与关注。" % (product_name, activity_name, term, unit, time, earning_percent, u"%", earning_aoumnt)
    return title, content


def msg_bid_fail(product_name):
    title = u"流标通知"
    content = u"感谢您投资 借款项目“%s”，该项目在有效期内未满标，视为流标，您的该笔投资金额已取消冻结，您可继续投资其他理财产品。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % product_name
    return title, content


def msg_register():
    title = u"注册成功"
    content = u"感谢您注册网利宝。 完成实名认证并充值。<br/><a href='/accounts/id_verify/' target='_blank'>点击完成实名认证</a><br/>感谢您对我们的支持与关注。<br/>网利宝"
    return title, content


def msg_bid_success(product_name, date):
    title = u"投标成功通知"
    content = u"感谢您投资 借款项目“%s”，该项目已满标放款，将于%s开始计息。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % (product_name, format_datetime(date, u"%Y年%m月%d日"))
    return title, content


def msg_pay_ok(amount):
    title = u"充值成功"
    content = u"您的网利宝账户已成功充值￥%s元，请查收。<br /><a href='/' target='_blank'>点击进行理财</a><br />感谢您对我们的支持与关注。<br />网利宝" % amount
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


def msg_bid_amortize(product_name, retime, amount):
    title = u"项目还款"
    content = u"借款项目“%s”于%s还款￥%s元，请注意查收。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注。<br/>网利宝" % (product_name, format_datetime(retime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content


def msg_bid_prepayment(product_name, retime, amount):
    title = u"提前还款"
    content = u"借款项目“%s”于%s提前还款￥%s元，请注意查收。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注。<br/>网利宝" % (product_name, format_datetime(retime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content


def msg_redpack_give(amount, name, dt):
    title = u"参与活动送红包"
    content = u"网利宝赠送的【%s】元【%s】已发放，请进入投资页面尽快投资赚收益吧！有效期至%s。<br/> <a href='/' target='_blank'>立即使用</a><br/>感谢您对我们的支持与关注。" % (amount, name, dt)
    return title,content


def msg_redpack_give_percent(amount, highest_amount, name, dt):
    title = u"参与活动送红包"
    if highest_amount == 0:
        str_tmp = ''
    else:
        str_tmp = u'最高抵扣【%s】元，' % highest_amount
    content = u"网利宝赠送的【%s】红包已发放，抵扣投资额的%s%%，%s请进入投资页面尽快投资赚收益吧！有效期至%s。<br/> <a href='/' target='_blank'>立即使用</a><br/>感谢您对我们的支持与关注。" % (name, amount, str_tmp, dt)
    return title, content


# 全民淘金短信站内信模板
@suffix
def sms_income(count, amount):
    return u"今日您共有{}个好友参与投资，为您产生的理财佣金{}元已发放，" \
           u"请进入我的账户-邀请奖励中查询！感谢您对我们的支持与关注。".format(count, amount)


def msg_give_income(count, amount):
    title = u"理财佣金到账通知"
    content = u"今日您共有{}个好友参与投资，为您产生的理财佣金{}元已发放，" \
              u"请进入<a href='/accounts/invite/'>我的账户-邀请奖励</a>中查询。<br/>" \
              u"感谢您对我们的支持与关注！<br/>网利宝".format(count, amount)
    return title, content


@suffix
def sms_alert_invest(name):
    return u"提醒投资：您的好友{}在网利宝看到几个超棒的理财计划，快来投资吧！".format(name)


@suffix
def sms_alert_invite(name, phone):
    return u"邀请注册：您的好友{}邀请您加入网利宝，快来一起赚钱，速速点击专属链接：" \
           u"https://www.wanglibao.com/activity/wap/share?phone={}".format(name, phone)

