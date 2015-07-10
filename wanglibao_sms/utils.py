# coding=utf-8
import json
import random
from django.conf import settings
import datetime
from django.utils import timezone
#from django.utils.module_loading import import_by_path
#from django.template.loader import render_to_string
from wanglibao_sms import messages, backends
from wanglibao_sms.models import PhoneValidateCode, ShortMessage, RateThrottle
import logging
logger = logging.getLogger(__name__)


def generate_validate_code():
    return "%d" % (random.randrange(100000, 1000000))

#channel sms, 0:auto 1:mandao 2:yimei
def send_messages(phones, messages, channel=0):
    # short_message = ShortMessage()

    if channel == 0:
        status, context = backends.ManDaoSMSBackEnd.send_messages(phones, messages)
        channel_val = u"慢道"
        #失败使用emay重发
        if status != 200:
            status, context = backends.EmaySMS.send_messages(phones, messages)
            channel_val = u"亿美"
    elif channel == 1:
        status, context = backends.ManDaoSMSBackEnd.send_messages(phones, messages)
        channel_val = u'慢道'
    else:
        status, context = backends.EmaySMS.send_messages(phones, messages)
        channel_val = u"亿美"

    if status != 200:
        result = u'失败'
    else:
        result = u'成功'

    context = json.dumps(context)
    arr = []
    for k,phone in enumerate(phones):
        arr.append(
            ShortMessage(phones=phone, contents=messages[k], channel=channel_val, status=result, context=context)
        )
    #for phone in phones:
    #    obj.append(
    #        ShortMessage(phones=phone, contents="|".join(messages), channel=channel_val, status=result, context=context)
    #    )
    ShortMessage.objects.bulk_create(arr)
    #backend = import_by_path(settings.SMS_BACKEND)
    #status, context = backend.send_messages(phones, messages)

    return status, context


def send_sms(phone, message):
    return send_messages([phone], [message])

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

def send_validation_code(phone, validate_code=None, ip=""):
    if validate_code is None:
        validate_code = generate_validate_code()
    if not check_rate(ip):
        return 403, u"已达到最大发送限制"

    now = timezone.now()
    code = PhoneValidateCode.objects.filter(phone=phone).first()
    if not code:
        code = PhoneValidateCode()
        code.phone = phone
        code.code_send_count = 1
        code.vcount = 1
    else:
        seconds = now - code.last_send_time
        seconds = seconds.total_seconds()
        if seconds <= 180:
            return 429, u"请180秒之后重试"
        if code.code_send_count >= 6:
            return 429, u"请联系客服进行验证"
        if code.code_send_count >= 4 and seconds < 86400:
            return 429, u"请24小时后进行重试"
        if code.code_send_count >= 2 and seconds < 3600:
            return 429, u"请1小时后进行重试"
        code.code_send_count += 1

    code.validate_code = validate_code
    code.last_send_time = now
    code.is_validated = False
    code.save()
    #try:
    #    phone_validate_code_item = PhoneValidateCode.objects.get(phone=phone)

    #    if (now - phone_validate_code_item.last_send_time) <= datetime.timedelta(seconds=60):
    #        return 429, u"请60秒之后重试"
    #    else:
    #        phone_validate_code_item.validate_code = validate_code
    #        phone_validate_code_item.last_send_time = now
    #        phone_validate_code_item.code_send_count += 1
    #        phone_validate_code_item.is_validated = False
    #        phone_validate_code_item.save()
    #except PhoneValidateCode.DoesNotExist:
    #    PhoneValidateCode.objects.create(
    #        phone=phone,
    #        validate_code=validate_code,
    #        last_send_time=now,
    #        code_send_count=1)

    status, message = send_sms(phone, messages.validate_code(validate_code))

    if status != 200:
        return status, message

    return 200, ''


def validate_validation_code(phone, code):
    status_code, message = 404, ''
    item = PhoneValidateCode.objects.filter(phone=phone).first()
    if not item:
        return status_code, message

    if item.vcount >= 3:
        return 410, "The maximum number of verify"
    if item.validate_code != code:
        item.vcount += 1
        item.save()
        return 410, "code error"
    now = timezone.now()
    if (now - item.last_send_time) >= datetime.timedelta(minutes=600):
        return 410, "code is expired"
    if item.is_validated:
        return 410, "code is validated"

    item.is_validated = True
    item.code_send_count = 0
    item.vcount = 0
    item.save()
    return 200, ""

    #try:
    #    phone_validate_item = PhoneValidateCode.objects.get(phone=phone)
    #    now = timezone.now()

    #    if phone_validate_item.validate_code == code:
    #        if (now - phone_validate_item.last_send_time) >= datetime.timedelta(minutes=30):
    #            status_code, message = 410, 'The code is expired'
    #        elif phone_validate_item.is_validated == True:
    #            status_code, message = 410, 'The code is validated'
    #        else:
    #            phone_validate_item.is_validated = True
    #            phone_validate_item.save()

    #            status_code, message = 200, ''

    #    else:
    #        pass

    #except PhoneValidateCode.DoesNotExist:
    #    pass

    #return status_code, message
