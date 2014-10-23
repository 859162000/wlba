# coding=utf-8
import json
import random
from django.conf import settings
import datetime
from django.utils import timezone
#from django.utils.module_loading import import_by_path
#from django.template.loader import render_to_string
from wanglibao_sms import messages, backends
from wanglibao_sms.models import PhoneValidateCode, ShortMessage
import logging
logger = logging.getLogger(__name__)


def generate_validate_code():
    return "%d" % (random.randrange(100000, 1000000))

#channel sms, 0:auto 1:mandao 2:yimei
def send_messages(phones, messages, channel=0):
    short_message = ShortMessage()
    short_message.phones = " ".join(phones)
    if len(phones) == len(messages):
        short_message.contents = " ".join([":".join(pair) for pair in zip(phones, messages)])
    else:
        short_message.contents = u"%s: %s" % (",".join(phones), "|".join(messages))
    short_message.save()
    #backend = import_by_path(settings.SMS_BACKEND)
    #status, context = backend.send_messages(phones, messages)

    if channel == 0:
        status, context = backends.ManDaoSMSBackEnd.send_messages(phones, messages)
        #失败使用emay重发
        if status != 200:
            status, context = backends.EmaySMS.send_messages(phones, messages)
    elif channel == 1:
        status, context = backends.ManDaoSMSBackEnd.send_messages(phones, messages)
    else:
        status, context = backends.EmaySMS.send_messages(phones, messages)

    if status != 200:
        short_message.status = u'失败'
    else:
        short_message.status = u'成功'

    short_message.context = json.dumps(context)
    short_message.save()

    return status, context


def send_sms(phone, message):
    return send_messages([phone], [message])

def send_rand_pass(phone, password):
    return send_messages([phone], [messages.rand_pass(password)])

def send_validation_code(phone, validate_code=None):
    if validate_code is None:
        validate_code = generate_validate_code()

    now = timezone.now()
    try:
        phone_validate_code_item = PhoneValidateCode.objects.get(phone=phone)

        if (now - phone_validate_code_item.last_send_time) <= datetime.timedelta(seconds=30):
            return 429, u"请60秒之后重试"
        else:
            phone_validate_code_item.validate_code = validate_code
            phone_validate_code_item.last_send_time = now
            phone_validate_code_item.code_send_count += 1
            phone_validate_code_item.save()
    except PhoneValidateCode.DoesNotExist:

        PhoneValidateCode.objects.create(
            phone=phone,
            validate_code=validate_code,
            last_send_time=now,
            code_send_count=1)

    status, message = send_sms(phone, messages.validate_code(validate_code))

    if status != 200:
        return status, message

    return 200, ''


def validate_validation_code(phone, code):
    status_code, message = 404, ''
    try:
        phone_validate_item = PhoneValidateCode.objects.get(phone=phone)
        now = timezone.now()

        if phone_validate_item.validate_code == code:
            if (now - phone_validate_item.last_send_time) >= datetime.timedelta(minutes=30):
                status_code, message = 410, 'The code is expired'

            else:
                phone_validate_item.is_validated = True
                phone_validate_item.save()

                status_code, message = 200, ''

        else:
            pass

    except PhoneValidateCode.DoesNotExist:
        pass

    return status_code, message
