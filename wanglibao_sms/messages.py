# coding=utf-8
import base64
import cPickle
from django.utils import timezone
from misc.models import Misc
from wanglibao_redis.backend import redis_backend

SMS_SIGN = u'【网利科技】'
SMS_SIGN_TD = u'退订回TD【网利科技】'
SMS_STR_WX = u' 关注网利宝服务号，每日签到抽大奖。'
SMS_STR_400 = u'如有疑问请致电网利宝客服电话：4008-588-066'


# zhoudong 重写该模块 2015/10/

# 在后台配置 Misc, key='message_switch', value='True' 使读取配置短信内容
def get_stitch():
    message_switch, status = Misc.objects.get_or_create(key='message_switch')
    return True if message_switch.value == 'True' else False


def format_datetime(time, fmt):
    return timezone.localtime(time).strftime(fmt.encode('utf-8')).decode('utf-8')


def suffix(f):
    def wrapper(*args, **kwargs):
        return unicode(f(*args, **kwargs)) + SMS_SIGN

    return wrapper


def suffix_td(f):
    def wrapper(*args, **kwargs):
        return unicode(f(*args, **kwargs)) + SMS_SIGN_TD

    return wrapper


@suffix
def deposit_succeed(name, amount):
    """
    充值成功
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('deposit_succeed')
            content = cPickle.loads(obj)['content']
            return content.format(name, amount)
        except Exception, e:
            print e
            return u'亲爱的{}，您的充值操作已成功，充值金额{}元。'.format(name, amount)
    else:
        return u'亲爱的{}，您的充值操作已成功，充值金额{}元。'.format(name, amount)


@suffix
def withdraw_failed(name, error_message=None):
    """
    提现失败
    """
    if get_stitch():
        try:
            redis = redis_backend()
            if len(error_message) < 1:
                obj = redis._get('withdraw_failed')
                content = cPickle.loads(obj)['content']
                return content.format(name)
            obj = redis._get('withdraw_failed_message')
            content = cPickle.loads(obj)['content']
            return content.format(name, error_message)
        except Exception, e:
            print e
            if len(error_message) < 1:
                return u'亲爱的{}，您的提现失败，请重新尝试。{}'.format(name, SMS_STR_400)
            return u'亲爱的{}，您的提现失败，原因如下：{}。{}'.format(name, error_message, SMS_STR_400)
    else:
        if len(error_message) < 1:
            return u'亲爱的{}，您的提现失败，请重新尝试。{}'.format(name, SMS_STR_400)
        return u'亲爱的{}，您的提现失败，原因如下：{}。{}'.format(name, error_message, SMS_STR_400)


@suffix
def withdraw_submitted(name):
    """
    提现申请成功
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('withdraw_submitted')
            content = cPickle.loads(obj)['content']
            return content.format(name)
        except Exception, e:
            print e
            return u'亲爱的{}，您的提现申请已受理，1-3个工作日内将处理完毕，请耐心等待。'.format(name)
    else:
        return u'亲爱的{}，您的提现申请已受理，1-3个工作日内将处理完毕，请耐心等待。'.format(name)


@suffix
def withdraw_confirmed(name, amount):
    """
    提现成功
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('withdraw_confirmed')
            content = cPickle.loads(obj)['content']
            return content.format(name, amount)
        except Exception, e:
            print e
            return u'亲爱的{}，您的提现已成功，提现金额：{}元，请注意查收！'.format(name, amount)
    else:
        return u'亲爱的{}，您的提现已成功，提现金额：{}元，请注意查收！'.format(name, amount)


@suffix
def product_settled(name, equity, product, settled_time):
    """
    投资成功
    """
    if product.pay_method.startswith(u"日计息"):
        stand = u'天'
    else:
        stand = u'个月'
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('product_settled')
            content = cPickle.loads(obj)['content']
            return content.format(
                name, product.name, equity.equity,
                format_datetime(settled_time, u'%Y年%m月%d日'), product.period, stand)
        except Exception, e:
            print e
            return u'亲爱的{}，您已成功投资{}项目 {}元，并于{}开始计息，期限{}{}，感谢您的支持！'.format(
                name, product.name, equity.equity,
                format_datetime(settled_time, u'%Y年%m月%d日'), product.period, stand
            )
    else:
        return u'亲爱的{}，您已成功投资{}项目 {}元，并于{}开始计息，期限{}{}，感谢您的支持！'.format(
            name, product.name, equity.equity,
            format_datetime(settled_time, u'%Y年%m月%d日'), product.period, stand
        )


@suffix
def product_failed(name, product):
    """
    投资失败
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('product_failed')
            content = cPickle.loads(obj)['content']
            return content.format(name,
                                  product.name,
                                  format_datetime(product.end_time, u'%Y年%m月%d日'))
        except Exception, e:
            print e
            return u'亲爱的{}，您投标的{}项目在{}之前未满标，投标失败。投标账款已退回到您的网利宝平台账户中。'.format(
                name, product.name, format_datetime(product.end_time, u'%Y年%m月%d日')
            )

    else:
        return u'亲爱的{}，您投标的{}项目在{}之前未满标，投标失败。投标账款已退回到您的网利宝平台账户中。'.format(
            name, product.name, format_datetime(product.end_time, u'%Y年%m月%d日')
        )

        # return u'%s[%s]在%s之前未满标，投标失败。投标账款已退回到您的网利宝平台账户中。' \
        #        % (product.short_name, product.serial_number, format_datetime(product.end_time, u'%Y年%m月%d日%H:%M'))


@suffix
def product_amortize(name, product, amount):
    """
    投资到账
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('product_amortize')
            content = cPickle.loads(obj)['content']
            return content.format(name, product.name, amount)
        except Exception, e:
            print e
            return u'亲爱的{}，您投资的{}项目收到还款{}元，已到账，请登录您的网利宝账户进行查看。'.format(
                name, product.name, amount
            )
    else:
        return u'亲爱的{}，您投资的{}项目收到还款{}元，已到账，请登录您的网利宝账户进行查看。'.format(
            name, product.name, amount
        )
        # return u'您投资的%s项目收到还款%s元，已到帐。请登录您的网利宝账户进行查看。' % (product.short_name, str(amount))


@suffix
def product_prepayment(name, product, amount):
    """
    提前还款到账
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('product_prepayment')
            content = cPickle.loads(obj)['content']
            return content.format(name, product.name, amount)
        except Exception, e:
            print e
            return u'亲爱的{}，您投资的{}项目收到还款{}元，已到账，请登录您的网利宝账户进行查看。'.format(
                name, product.name, amount
            )

    else:
        return u'亲爱的{}，您投资的{}项目收到还款{}元，已到账，请登录您的网利宝账户进行查看。'.format(
            name, product.name, amount
        )
        # return u'您投资的%s项目已提前还款%s元，已到帐。请登录您的网利宝账户进行查看。' % (product.short_name, str(amount))


@suffix
def validate_code(code):
    """
    手机验证码
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('product_settled')
            content = cPickle.loads(obj)['content']
            return content.format(code)
        except Exception, e:
            print e
            return u'您的验证码为：{}，请尽快完成操作。'.format(code)

    else:
        return u'您的验证码为：{}，请尽快完成操作。'.format(code)


@suffix
def rand_pass(password):
    """
    发送随机密码
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('rand_pass')
            content = cPickle.loads(obj)['content']
            return content.format(password)
        except Exception, e:
            print e
            return u'感谢注册网利宝，您的初始密码是{}，请登录wanglibao.com修改密码。'.format(password)
    else:
        return u'感谢注册网利宝，您的初始密码是{}，请登录wanglibao.com修改密码。'.format(password)


@suffix
def earning_message(name, amount):
    """
    投标奖励
    :param amount:
    :return:
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('earning_message')
            content = cPickle.loads(obj)['content']
            return content.format(name, amount)
        except Exception, e:
            print e
            return u'亲爱的{}，您的投标奖励{}%收益，已赠送到您的网利宝账户，' \
                   u'可用于理财投资。详情请登陆网利宝查看站内信。'.format(name, amount)

    else:
        return u'亲爱的{}，您的投标奖励{}%收益，已赠送到您的网利宝账户，可用于理财投资。详情请登陆网利宝查看站内信。'.format(name, amount)


@suffix_td
def red_packet_get_alert(amount, rtype):
    """
    红包、加息券获得 提醒
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('red_packet_get_alert')
            content = cPickle.loads(obj)['content']
            return content.format(amount, rtype)
        except Exception, e:
            print e
            return u'{}{}已经存入您的账户，登录网利宝账户进行查看。{}'.format(amount, rtype, SMS_STR_WX)
    else:
        return u'{}{}已经存入您的账户，登录网利宝账户进行查看。{}'.format(amount, rtype, SMS_STR_WX)


@suffix_td
def red_packet_invalid_alert(count, days):
    """
    红包、加息券快过期前3天提醒
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('red_packet_invalid_alert')
            content = cPickle.loads(obj)['content']
            return content.format(count)
        except Exception, e:
            print e
            return u'温馨提示，您有{}张理财券再过{}天就要过期了，请尽快登录网利宝官网或者app使用！{}'.format(count, days, SMS_STR_WX)
    else:
        return u'温馨提示，您有{}张理财券再过{}天就要过期了，请尽快登录网利宝官网或者app使用！{}'.format(count, days, SMS_STR_WX)


@suffix_td
def user_invest_alert():
    """
    注册3天后未投资用户的提醒短信
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('user_invest_alert')
            content = cPickle.loads(obj)['content']
            return content
        except Exception, e:
            print e
            return u'就差1步您的新手红包/加息券就能为您赚钱啦！登录官网或APP抢新手专享16%高收益，使用理财券更可收益翻倍哦！'
    else:
        return u'就差1步您的新手红包/加息券就能为您赚钱啦！登录官网或APP抢新手专享16%高收益，使用理财券更可收益翻倍哦！'


@suffix
def product_full_message(name):
    return u'%s，满标了。' % name


# 站内信模板
def msg_bid_purchase(order_id, product_name, amount):
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('msg_bid_purchase')
            title = cPickle.loads(obj)['title']
            content = cPickle.loads(obj)['content']
            return title, content.format(order_id, product_name, amount)
        except Exception, e:
            title = u"投标通知"
            content = u"感谢您投资订单号【%s】借款项目“%s”￥%s元，该项目正在招标中，您的投标资金暂时被冻结，满标后将放款计息。" \
                      u"<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" \
                      % (order_id, product_name, amount)
            return title, content
    else:
        title = u"投标通知"
        content = u"感谢您投资订单号【%s】借款项目“%s”￥%s元，该项目正在招标中，您的投标资金暂时被冻结，满标后将放款计息。" \
                  u"<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" \
                  % (order_id, product_name, amount)
    return title, content


def msg_bid_earning(product_name, activity_name, term, time, earning_percent, earning_aoumnt, unit):
    title = u"活动收益"
    content = u"借款项目“%s(%s），期限%s%s”于%s赠送【%s%s】活动收益【%s】元，请注意查收。 " \
              u"<a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注。" \
              % (product_name, activity_name, term, unit, time, earning_percent, u"%", earning_aoumnt)
    return title, content


def msg_bid_fail(product_name):
    title = u"流标通知"
    content = u"感谢您投资借款项目“%s”，该项目在有效期内未满标，视为流标，您的该笔投资金额已取消冻结，您可继续投资其他理财产品。<br/>" \
              u"<a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" \
              % product_name
    return title, content


def msg_register():
    title = u"注册成功"
    content = u"感谢您注册网利宝。 完成实名认证并充值。<br/><a href='/accounts/id_verify/' target='_blank'>" \
              u"点击完成实名认证</a><br/>感谢您对我们的支持与关注。<br/>网利宝"
    return title, content


def msg_bid_success(product_name, date):
    title = u"投标成功通知"
    content = u"感谢您投资 借款项目“%s”，该项目已满标放款，将于%s开始计息。<br/>" \
              u"<a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" \
              % (product_name, format_datetime(date, u"%Y年%m月%d日"))
    return title, content


def msg_pay_ok(amount):
    title = u"充值成功"
    content = u"您的网利宝账户已成功充值￥%s元，请查收。<br /><a href='/' target='_blank'>点击进行理财</a><br />" \
              u"感谢您对我们的支持与关注。<br />网利宝" % amount
    return title, content


def msg_withdraw(withtime, amount):
    title = u"申请提现"
    content = u"您于%s申请的提现￥%s元已经提交，如您填写的账户信息正确无误，您的资金将会于3个工作日内到达您的银行账户。<br/>" \
              u"<a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" \
              % (format_datetime(withtime, u"%Y年%m月%d日%H:%M:%S"), amount)
    # redis = redis_backend()
    # obj = redis._get('msg_withdraw')
    # title = cPickle.loads(obj)['content']
    # content = cPickle.loads(obj)['content']
    return title, content


def msg_withdraw_fail(withtime, amount):
    title = u"提现结果"
    content = u"您于%s申请的提现￥%s元，由于您填写的银行账户信息有误，未能成功汇款。请您填写正确的银行账户信息，重新提交申请。<br/>" \
              u"<a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>感谢您对我们的支持与关注！<br/>网利宝" \
              % (format_datetime(withtime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content


def msg_withdraw_success(withtime, amount):
    """
    提现成功
    """
    title = u"提现成功"
    content = u"您于%s申请的提现￥%s元，已汇款，请注意查收。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>" \
              u"感谢您对我们的支持与关注！<br/>网利宝" % (format_datetime(withtime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content


def msg_bid_amortize(product_name, retime, amount):
    title = u"项目还款"
    content = u"借款项目“%s”于%s还款￥%s元，请注意查收。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>" \
              u"感谢您对我们的支持与关注。<br/>网利宝" % (product_name, format_datetime(retime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content


def msg_bid_prepayment(product_name, retime, amount):
    title = u"提前还款"
    content = u"借款项目“%s”于%s提前还款￥%s元，请注意查收。<br/><a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>" \
              u"感谢您对我们的支持与关注。<br/>网利宝" % (product_name, format_datetime(retime, u"%Y年%m月%d日%H:%M:%S"), amount)
    return title, content


def msg_redpack_give(amount, name, dt):
    title = u"参与活动送红包"
    content = u"网利宝赠送的【%s】元【%s】已发放，请进入投资页面尽快投资赚收益吧！有效期至%s。<br/> " \
              u"<a href='/' target='_blank'>立即使用</a><br/>感谢您对我们的支持与关注。" % (amount, name, dt)
    return title, content


def msg_redpack_give_percent(amount, highest_amount, name, dt):
    title = u"参与活动送红包"
    if highest_amount == 0:
        str_tmp = ''
    else:
        str_tmp = u'最高抵扣【%s】元，' % highest_amount
    content = u"网利宝赠送的【%s】红包已发放，抵扣投资额的%s%%，%s请进入投资页面尽快投资赚收益吧！有效期至%s。<br/> " \
              u"<a href='/' target='_blank'>立即使用</a><br/>感谢您对我们的支持与关注。" % (name, amount, str_tmp, dt)
    return title, content


# 全民淘金短信站内信模板
@suffix_td
def sms_income(name, count, amount):
    return u"亲爱的{}，今日您共有{}个好友参与投资，为您产生的理财佣金为{}元已发放，" \
           u"请进入我的账户－全民淘金中查询！感谢您的支持。".format(name, count, amount)
    # redis = redis_backend()
    # obj = redis._get('sms_income')
    # content = cPickle.loads(obj)['content']
    # return content.format(count, amount)


def msg_give_income(count, amount):
    title = u"理财佣金到账通知"
    content = u"今日您共有{}个好友参与投资，为您产生的理财佣金{}元已发放，" \
              u"请进入<a href='/accounts/invite/'>我的账户-全民淘金</a>中查询。<br/>" \
              u"感谢您对我们的支持与关注！<br/>网利宝".format(count, amount)
    return title, content


@suffix_td
def sms_alert_invest(name):
    return u"{}在网利宝看到几个超棒的理财计划，你也赶紧去投资，不要再错失良机啦！{}".format(name, SMS_STR_WX)


@suffix_td
def sms_alert_invite(name, phone):
    return u"邀请注册：您的好友{}邀请您加入网利宝一起投资赚钱，注册就有惊喜。速速点击专属链接：" \
           u"https://www.wanglibao.com/aws?p={} ".format(name, base64.b64encode(phone)[0:-1])
    # u"https://www.wanglibao.com/activity/wap/share?phone={} ".format(name, phone)


def msg_give_coupon(name, amount, end_time):
    title = u"参与活动送加息券"
    content = u"网利宝赠送的【{}】加息券已发放，加息额度{}%，请进入投资页面尽快投资赚收益吧！有效期至{}。" \
              u"<a href='/'>立即使用</a>。<br/>" \
              u"感谢您对我们的支持与关注！<br/>网利宝".format(name, amount, end_time)
    return title, content


def sms_alert_unbanding_xunlei(reward_dsct, url):
    content = u"由于您之前没有完成迅雷帐号登录，无法关联，导致会员奖励无法到帐。<br/>" \
              u"请先到以下页面完成迅雷帐号登录，即可获得{}奖励。" \
              u"<br/>" \
              u"<a href='{}'>领取奖励>></a><br/>"
    return content.format(reward_dsct, url)


@suffix
def changed_mobile_success():
    """
    修改手机号成功短信
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('changed_mobile_success')
            content = cPickle.loads(obj)['content']
            return content
        except Exception:
            return u"尊敬的网利宝用户，您已成功修改绑定新手机号，请使用新的手机号进行登陆，密码与原登录密码相同。感谢您的支持。"
    else:
        return u"尊敬的网利宝用户，您已成功修改绑定新手机号，请使用新的手机号进行登陆，密码与原登录密码相同。感谢您的支持。"


@suffix
def changed_mobile_fail():
    """
    修改手机号失败短信
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('changed_mobile_fail')
            content = cPickle.loads(obj)['content']
            return content
        except Exception:
            return u"尊敬的网利宝用户，由于所上传的资料不符要求，您的修改手机号申请未通过，请按照要求上传资料文件或联系客服，感谢您的支持。"
    else:
        return u"尊敬的网利宝用户，由于所上传的资料不符要求，您的修改手机号申请未通过，请按照要求上传资料文件或联系客服，感谢您的支持。"


@suffix
def experience_amortize(name, amount):
    """
    投资到账
    :param name:
    :param amount:
    """
    if get_stitch():
        try:
            redis = redis_backend()
            obj = redis._get('experience_amortize')
            content = cPickle.loads(obj)['content']
            return content.format(name, amount)
        except Exception, e:
            print e
            return u'亲爱的{}，您投资的体验金项目收到还款{}元，已到账，请登录您的网利宝账户进行查看。'.format(name, amount)
    else:
        return u'亲爱的{}，您投资的体验金项目收到还款{}元，已到账，请登录您的网利宝账户进行查看。'.format(name, amount)


def experience_amortize_msg(name, product_name, period, settlement_time, amount):
    title = u"项目还款"
    content = u"亲爱的{}您好:体验金项目“{}”,期限{}天于{}还款{}元，请注意查收。<br/>" \
              u"<a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>" \
              u"感谢您对我们的支持与关注。<br/>网利宝".format(name, product_name, period, format_datetime(settlement_time, u"%Y年%m月%d日"), amount)
    return title, content


if __name__ == "__main__":
    print sms_alert_invest('test')
    print sms_alert_invite('test', '15038038823')
