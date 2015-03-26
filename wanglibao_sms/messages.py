# coding=utf-8
from datetime import timedelta
from django.utils import timezone

def format_datetime(time, fmt):
    return timezone.localtime(time).strftime(fmt.encode('utf-8')).decode('utf-8')


def suffix(f):
    def wrapper(*args, **kwargs):
        return unicode(f(*args, **kwargs)) + u'回复TD退订 4008-588-066【网利宝】'
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
    return u'您投资的%s项目收到还款%s元，已到帐。' % (product.short_name,
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
def jiuxian_invited(money):
    return u'感谢您在网利宝完成首次理财！您的注册手机号将于3个工作日内收到%s元话费，请查收。回复TD退订 4008-588-066' \
           % money

@suffix
def gift_first_buy(money):
    return u'感谢您在网利宝完成首次理财！您的注册手机号将于3个工作日内收到%s元话费，请查收。回复TD退订 4008-588-066' \
           % money

@suffix
def rand_pass(password):
    return u'感谢注册网利宝，您的初始密码是%s，请登录wanglibao.com修改密码。' % password

@suffix
def earning_message(amount):
    return u'亲，您的投标奖励%s%s收益，已赠送到您的网利宝账户，可用于理财投资。详情请登陆网利宝查看站内信。' % (amount, u'%')

@suffix
def product_full_message(name):
    return u'%s，满标了。' % name

@suffix
def redpack_give(amount, name, dt):
    return u'您的账户获得【%s】奖励【%s】元。有效期至%s。' % (name, amount, dt)

#站内信模板
def msg_bid_purchase(order_id, product_name, amount):
    title = u"投标通知"
    content = u"感谢您投资订单号【%s】借款项目“%s”￥%s元，该项目正在招标中，您的投标资金暂时被冻结，满标后将放款计息。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % (order_id, product_name, amount)
    return title, content

def msg_bid_earning(product_name, activity_name, term, time, earning_percent, earning_aoumnt):
    title = u"活动收益"
    content = u"借款项目“%s(%s）,期限%s个月”于%s赠送【%s%s】活动收益【%s】元，请注意查收。 查看账户余额 感谢您对我们的支持与关注。" % (product_name, activity_name, term, time, earning_percent, u"%", earning_aoumnt)
    return title, content

def msg_bid_fail(product_name):
    title = u"流标通知"
    content = u"感谢您投资 借款项目“%s”，该项目在有效期内未满标，视为流标，您的该笔投资金额已取消冻结，您可继续投资其他理财产品。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % product_name
    return title, content

def msg_register():
    title = u"注册成功"
    content = u"感谢您注册网利宝。 完成实名认证并充值。<br/><a href='/accounts/id_verify/' target='_blank'>点击此处完成实名认证</a><br/>感谢您对我们的支持与关注。<br/>网利宝"
    return title, content

#风行过来的注册成功
def msg_register_f():
    title = u"注册成功"
    content = u"感谢您注册网利宝。 完成实名认证并充值成功，免费领取7天风行VIP会员。<br/> <a href='/accounts/id_verify/' target='_blank'>点击此处完成实名认证</a></br/> 感谢您对我们的信任与支持。<br/> 网利宝"
    return title, content

def msg_register_authok(activation):
    title = u"注册成功"
    content = u"感谢您注册网利宝。<br/>网利宝赠送您3天迅雷白金会员激活码，请您查收！<br/>激活码：%s，有效期至2015年12月31日。<br/>立即兑换（<a href='http://act.vip.xunlei.com/vip/2014/xlhyk/' target='_blank'>http://act.vip.xunlei.com/vip/2014/xlhyk/</a>）<br/>感谢您对我们的支持与关注。<br/>网利宝" % activation
    return title, content

def msg_despoit_ok(activation):
    title = u"充值成功"
    content = u"恭喜您充值成功，赠送给您的3天迅雷白金会员激活码：%s，有效期至2015年12月31日。<br/>参加精彩活动，享受1%%额外收益，<a href='/' target='_blank'>立即购买赚钱</a><br/>感谢您对我们的支持与关注。<br/>网利宝" % activation
    return title, content

def msg_despoit_ok_7(activation):
    title = u"充值成功"
    content = u"恭喜您充值成功，赠送给您的7天迅雷白金会员激活码：%s，有效期至2015年12月31日。<br/>参加精彩活动，享受1%%额外收益，<a href='/' target='_blank'>立即购买赚钱</a><br/>感谢您对我们的支持与关注。<br/>网利宝" % activation
    return title, content

def msg_validate_ok(activation):
    title = u"实名认证成功"
    content = u"恭喜您完成实名认证，赠送给您的3天迅雷白金会员激活码：%s，有效期至2015年12月31日。<br/>参加精彩活动，享受1%%额外收益，<a href='/pay/banks/' target='_blank'>立即充值赚钱</a><br/>感谢您对我们的支持与关注。<br/>网利宝" % activation
    return title, content


def msg_validate_ok2(activation):
    title = u"实名认证成功"
    content = u"恭喜您完成实名认证，赠送给您的50G快盘会员激活码：%s，有效期至2015年12月31日。<a href='http://www.kuaipan.cn/n/user/records/lottery'>兑换快盘激活码</a><br/><a href='/pay/banks/' target='_blank'>立即充值</a><br/>感谢您对我们的支持与关注。<br/>网利宝" % activation
    return title, content

def msg_validate_fake():
    title = u"实名认证成功"
    content = u"恭喜您完成实名认证，请您使用注册手机号码向客服索要7天迅雷白金会员激活码。<br/>参加精彩活动，享受1%%额外收益，<a href='/pay/banks/' target='_blank'>立即充值赚钱</a><br/>感谢您对我们的支持与关注。<br/>网利宝"
    return title, content

#迅雷会员
def msg_first_licai(activation):
    title = u"活动期首次理财成功"
    content = u"感谢您在活动期间完成首次理财。<br/>网利宝赠送您1个月迅雷白金会员激活码，请您查收！<br/>激活码：%s，有效期至2015年12月31日。<br/>立即兑换（<a href='http://act.vip.xunlei.com/vip/2014/xlhyk/' target='_blank'>http://act.vip.xunlei.com/vip/2014/xlhyk/</a>）<br/>感谢您对我们的支持与关注。<br/>网利宝" % activation
    return title, content


#金山快盘
def msg_first_kuaipan(size, activation):
    title = u"活动期理财成功"
    content = u"感谢您在活动期间完成首次理财。<br/>网利宝赠送您%s快盘网盘，请您查收！<br/>激活码：%s，有效期至2015年12月31日。<br/><a href='http://www.kuaipan.cn/n/user/records/lottery' target='_blank'>立即兑换</a><br/>感谢您对我们的支持与关注。<br/>网利宝" % (size, activation)
    return title, content

#风行会员
def msg_first_fengxing(activation):
    title = u"活动期首次理财成功"
    content = u"感谢您在活动期间完成首次理财。<br/> 网利宝赠送您1个月风行VIP会员，请您查收！<br/> 激活码：%s，有效期至2015年12月31日。<br/> <a href='http://www.fun.tv/vip/pay/v/coupon' target='_blank'>激活会员</a><br/> 感谢您对我们的信任与支持。<br/> 网利宝" % activation
    return title, content

def msg_invite_major(inviter, invited):
    title = u"邀请好友送话费"
    content = u"您的好友%s已通过您的邀请完成网利宝投资，您和您好友将共享60元话费,您的30元话费将于3个工作日内充值至您的手机号%s，请注意查收。<br/>感谢您对我们的支持与关注！<br/>网利宝" % (invited, inviter)
    return title, content

def msg_invite_are(inviter, invited):
    title = u"邀请好友送话费"
    content = u"您已和您的好友%s成功建立邀请关系，您和您好友将共享60元话费,您的30元话费将于3个工作日内充值至您的手机号%s，请注意查收。<br/>感谢您对我们的支持与关注！<br/>网利宝" % (inviter, invited)
    return title, content

#网利宝其他渠道首次投资送话费
def msg_first_buy():
    title = u"邀请好友送话费"
    content = u"您已完成网利宝投资，您的30元话费奖励将于3个工作日内充值至您的注册手机号，请注意查收。<br/>感谢您对我们的支持与关注！<br/>网利宝"
    return title, content

def msg_jiuxian():
    title = u"邀请好友送话费"
    content =  u'亲爱的您好：<br>感谢您在网利宝完成首次理财！您的注册手机号将于3个工作日内收到30元话费，请查收。<br/>感谢您对我们的支持与关注！网利宝'
    return title, content

def msg_bid_success(product_name, date):
    title = u"投标成功通知"
    content = u"感谢您投资 借款项目“%s”，该项目已满标放款，将于%s开始计息。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" % (product_name, format_datetime(date, u"%Y年%m月%d日"))
    return title, content

def msg_pay_ok(amount):
    title = u"充值成功"
    # content = u"您的网利宝账户已成功充值￥%s元，请查收。<br/>活动1：投资不同产品，即送1个月迅雷白金会员或10G、50G、100G快盘网盘。<br/>活动2：参加精彩活动，额外获赠1%%年化收益奖励。<br/>活动3：理财达到一定额度“迅雷白金会员、话费、京东卡、iPad、iPhone6、iPhone6 Plus”送不停。<br/>活动4：邀请好友完成首次单笔200元理财，双方共享60元话费。<br/><a href='/' target='_blank'>点击此处进行理财</a><br/>感谢您对我们的支持与关注。<br/>网利宝" % amount
    content = u"您的网利宝账户已成功充值￥%s元，请查收。<br /><a href='/' target='_blank'>点击此处进行理财</a><br />感谢您对我们的支持与关注。<br />网利宝" % amount
    return title, content

def msg_pay_ok_f(amount, activation):
    title = u"充值成功"
    content = u"恭喜您完成充值，您的网利宝账户已成功充值￥%s元，请查收。网利宝赠送给您的7天风行VIP会员：%s，有效期至2015年12月31日。<a href='http://www.fun.tv/vip/pay/v/coupon' target='_blank'>激活会员</a><br/> 活动期间：即日起-2015年1月31日<br/> 活动1：首次投资任意P2P产品，即送礼包。<br/> 活动2：参加精彩活动，额外获赠1%%年化收益奖励。<br/> 活动3：理财达到一定额度“风行VIP会员、话费、京东卡、iPad、iPhone6、iPhone6 Plus”送不停。<br/> 活动4：邀请好友完成首次单笔200元理财，双方共享60元话费。<br/> <a href='/' target='_blank'>立即投资</a><br/> 感谢您对我们的信任与支持。<br/> 网利宝" % (amount, activation)
    return title, content

def msg_pay_ok_f_2(amount):
    title = u"充值成功"
    content = u"恭喜您完成充值，您的网利宝账户已成功充值￥%s元，请查收。" % amount
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

#满额送京东卡
def msg_invest_jdcard(total, nominal, activation):
    title = u"满额送京东卡"
    content = u"您在“满额就送”活动期间，累计投资%s元，根据活动规则，您获得%s元京东卡奖励。<br/>京东卡密码：%s,请注意查收。<br/>感谢您对我们的支持与关注！<br/>网利宝" % (total, nominal, activation)
    return title, content

def msg_redpack_give(amount, name, dt):
    title = u"参与活动送红包"
    content = u"网利宝赠送的【%s】元【%s】已发放，请进入投资页面尽快投资赚收益吧！有效期至%s。<br/> <a href='/' target='_blank'>立即使用</a><br/>感谢您对我们的支持与关注。" % (amount, name, dt)
    return title,content


def msg_sevenday_iqiyi(activation):
    title = u"充值送7天爱奇艺会员"
    content = u"感谢您在活动期间完成充值。<br/>网利宝赠送您7天爱奇艺会员，会员码为：%s，请注意查收。<br/>感谢您对我们的信任与支持！<br/>网利宝" % activation
    return title, content


def msg_month_iqiyi(activation):
    title = u"首次投资送一个月爱奇艺会员"
    content = u"感谢您在活动期间完成首次投资。<br/>网利宝赠送您一个月爱奇艺会员，会员码为：%s，请注意查收。<br/>感谢您对我们的信任与支持！<br/>网利宝" % activation
    return title, content


def msg_month_pptv(activation):
    title = u"实名认证送一个月PPTV会员"
    content = u"感谢您在活动期间完成实名认证。<br/>网利宝赠送您一个月PPTV会员，会员码为：%s，有效期至2015年4月25日，请注意查收。<a href='http://pay.vip.pptv.com/vipcard/' target='_blank'>使用地址</a><br/>感谢您对我们的信任与支持！<br/>网利宝" % activation
    return title, content
