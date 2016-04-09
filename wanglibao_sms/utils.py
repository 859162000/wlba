# coding=utf-8
import json
import random, math
# from django.conf import settings
import datetime
from django.utils import timezone
from wanglibao_sms import messages, backends
from wanglibao_sms.models import PhoneValidateCode, ShortMessage, RateThrottle
import logging
logger = logging.getLogger(__name__)


def generate_validate_code():
    return "%d" % (random.randrange(100000, 1000000))


def send_messages(phones, messages, channel=0, ext=''):
    # short_message = ShortMessage()
    status, context = backends.ManDaoSMSBackEnd.send_messages(phones, messages, ext)
    channel_val = u"慢道"
    # if channel == 0:
    #     status, context = backends.ManDaoSMSBackEnd.send_messages(phones, messages, ext)
    #     channel_val = u"慢道"
    #     # 失败使用emay重发
    #     if status != 200:
    #         status, context = backends.EmaySMS.send_messages(phones, messages)
    #         channel_val = u"亿美"
    # elif channel == 1:
    #     status, context = backends.ManDaoSMSBackEnd.send_messages(phones, messages, ext)
    #     channel_val = u'慢道'
    # else:
    #     status, context = backends.EmaySMS.send_messages(phones, messages)
    #     channel_val = u"亿美"

    if status != 200:
        result = u'失败'
    else:
        result = u'成功'

    context = json.dumps(context)
    arr = []
    if len(phones) != len(messages):
        messages *= len(phones)
    for k, phone in enumerate(phones):
        arr.append(
            ShortMessage(phones=phone, contents=messages[k], channel=channel_val, status=result, context=context)
        )
    ShortMessage.objects.bulk_create(arr)
    return status, context


def send_sms(phone, message, ext=''):
    return send_messages([phone], [message], ext=ext)


def send_rand_pass(phone, password):
    return send_messages([phone], [messages.rand_pass(password)])


def check_rate(ip):
    if not ip:
        return True
    rate = RateThrottle.objects.filter(ip=ip).first()
    if not rate:
        rate = RateThrottle()
        rate.ip = ip
        rate.send_count = 1
        rate.last_send_time = timezone.now()
        rate.save()
        return True
    else:
        now = timezone.now()
        gap = now - rate.last_send_time
        seconds = gap.total_seconds()
        if seconds <= 60:
            rate.send_count += 1
            if rate.send_count > rate.max_count:
                return False
        else:
            rate.send_count = 1
            rate.last_send_time = now
        rate.save()
        return True


def send_validation_code(phone, validate_code=None, ip="", ext=''):
    """
    # Modify by hb on 2015-12-01
    # 1分钟内只能获取1次
    # 1小时内只能连续获取3次——所谓“连续获取”是指获取了验证码但没有输入验证，一旦验证成功则连续获取次数code_send_count会清零
    # 24小时内只能连续获取6次
    # 连续获取10次而没有输入验证会被锁定，必须通过后台或者客服进行重置
    # 同一个短信验证码连续输入3次错误会提示“短信码连续输入错误达到3次，请重新获取”，重新获取后错误次数vcount会清零
    # 短信验证码的失效时间为10分钟，10分钟内重复获取将返回相同的短信码，输入正确或者10分钟后获取将返回新的短信验证码
    # 同一个IP在1分钟内只能获取10次验证码（无论是否使用），超出10次则无法获取（特指在调用参数包含IP地址的情形，目前暂未投入应用）
    :param phone:  # 手机号
    :param validate_code: # 验证码
    :param ip: # IP地址
    :param ext: # 短信通道内部渠道代码标识, 应用类不加标识, 发送注册短信加777
    :return status, message
    """
    if validate_code is None:
        validate_code = generate_validate_code()
    if not check_rate(ip):
        return 403, u"操作太频繁了，休息一下"

    now = timezone.now()
    code = PhoneValidateCode.objects.filter(phone=phone).first()
    if not code:
        code = PhoneValidateCode()
        code.phone = phone
        code.validate_code = validate_code
        code.code_send_count = 0
        code.vcount = 0
        code.create_time = now
    else:
        seconds = now - code.last_send_time
        seconds = seconds.total_seconds()

        if code.code_send_count >= 10:
            return 429, u'请联系客服进行验证'
        if code.code_send_count >= 6 and seconds < 86400:
            # return 429, u'3-请24小时后重试'
            return 429, u'请{0}小时后重试'.format(int(((86400-seconds)//3600)+1))
        if code.code_send_count >= 3 and seconds < 3600:
            # return 429, u'4-请60分钟后重试'
            return 429, u'请{0}分钟后重试'.format(int(((3600-seconds)//60)+1))
        if seconds <= 60:
            return 429, u'请60秒之后重试'

        valid_seconds = now - code.create_time
        valid_seconds = valid_seconds.total_seconds()
        if valid_seconds <= 60 * 10 and code.vcount >= 5:
            # return 429, u'5-请10分钟后重新获取'
            return 429, u'请{0}分钟后重新获取'.format(int(((600-valid_seconds)//60)+1))
        if valid_seconds <= 60 * 10 and not code.is_validated:
            validate_code = code.validate_code
        else:
            code.validate_code = validate_code
            code.vcount = 0
            code.create_time = now

    code.code_send_count += 1
    code.last_send_time = now
    code.is_validated = False
    code.save()

    status, message = send_sms(phone, messages.validate_code(validate_code), ext=ext)
    if status != 200:
        return status, message

    return 200, ''


# Modify by hb on 2015-12-01
def validate_validation_code(phone, code):
    status_code, message = 404, u'短信验证码不存在，请重新获取'
    item = PhoneValidateCode.objects.filter(phone=phone).first()
    if not item:
        return status_code, message

    now = timezone.now()
    if (now - item.create_time) >= datetime.timedelta(minutes=30):
        return 410, u'短信验证码错误，请重新获取'
    if (now - item.create_time) >= datetime.timedelta(minutes=10):
        return 410, u'短信验证码已经过期，请重新获取'
    if item.is_validated:
        return 410, u'短信验证码已经被使用，请重新获取'
    if item.vcount >= 5:
        return 410, u'验证码错误频繁，请稍后再获取'

    if item.validate_code != code:
        item.vcount += 1
        item.last_validate_time = now
        item.save()
        return 410, u'短信验证码输入错误，请重新输入'

    item.is_validated = True
    item.code_send_count = 0
    item.vcount = 0
    item.last_validate_time = now
    item.save()

    return 200, ""
